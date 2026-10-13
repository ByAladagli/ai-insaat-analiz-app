import io
import logging
import math
import os
import re
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image, UnidentifiedImageError

from ai_engine import analyze_land
from pdf_generator import generate_feasibility_report

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("ai-insaat-api")

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
REPORT_DIR = BASE_DIR / "reports"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_FORMATS = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}
REPORT_NAME_RE = re.compile(r"^[0-9a-f]{32}\.pdf$")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="AI İnşaat Analiz API",
    version="1.1.0",
    description="Ön fizibilite prototipi; resmî imar görüşü veya yatırım tavsiyesi değildir.",
)

allowed_origins = [
    item.strip()
    for item in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if item.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def _validate_image(filename: str, data: bytes) -> None:
    extension = Path(filename or "").suffix.lower()
    expected_format = ALLOWED_FORMATS.get(extension)
    if not expected_format or not data:
        raise HTTPException(status_code=415, detail="Yalnızca JPG, PNG veya WebP görselleri kabul edilir.")
    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.format != expected_format:
                raise HTTPException(status_code=415, detail="Dosya uzantısı ve görsel biçimi eşleşmiyor.")
            image.verify()
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=415, detail="Dosya geçerli bir görsel değil.")


@app.get("/health")
async def health():
    return {"ok": True, "service": "ai-insaat-analiz-api", "version": app.version}


@app.post("/analyze")
async def process_land(
    image: UploadFile = File(...),
    location: str = Form(...),
    area_sqm: float = Form(...),
):
    location = location.strip()
    if not location or len(location) > 300:
        raise HTTPException(status_code=422, detail="Konum 1-300 karakter olmalıdır.")
    if not math.isfinite(area_sqm) or area_sqm <= 0 or area_sqm > 100_000_000:
        raise HTTPException(status_code=422, detail="Arsa alanı 0 ile 100.000.000 m² arasında geçerli bir sayı olmalıdır.")

    image_id = uuid.uuid4().hex
    suffix = Path(image.filename or "").suffix.lower()
    image_path = UPLOAD_DIR / f"{image_id}{suffix}"
    report_path = REPORT_DIR / f"{image_id}.pdf"

    try:
        data = await image.read(MAX_UPLOAD_BYTES + 1)
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Görsel en fazla 10 MB olabilir.")
        _validate_image(image.filename or "", data)

        image_path.write_bytes(data)
        analysis_result = await analyze_land(str(image_path), location, area_sqm)
        analysis_result["report_notice"] = (
            "Bu çıktı yaklaşık varsayımlara dayalı ön fizibilitedir. Resmî imar verisi, "
            "parsel sınırı, plan notları veya görselden otomatik ölçüm doğrulaması yapılmamıştır."
        )
        generate_feasibility_report(analysis_result, str(report_path))
        if not report_path.is_file() or report_path.stat().st_size == 0:
            raise RuntimeError("PDF oluşturuldu olarak bildirildi ancak dosya yok veya boş.")

        return JSONResponse(content={
            "success": True,
            "data": analysis_result,
            "pdf_url": f"/download-report/{report_path.name}",
        })
    except HTTPException:
        raise
    except Exception:
        logger.exception("Arsa analizi başarısız")
        report_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Analiz tamamlanamadı. Sunucu kayıtlarını kontrol edin.")
    finally:
        image_path.unlink(missing_ok=True)
        await image.close()


@app.get("/download-report/{filename}")
async def download_report(filename: str):
    if not REPORT_NAME_RE.fullmatch(filename):
        raise HTTPException(status_code=400, detail="Geçersiz rapor adı.")
    path = REPORT_DIR / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Rapor bulunamadı veya süresi doldu.")
    return FileResponse(path, media_type="application/pdf", filename="Arsa_On_Fizibilite_Raporu.pdf")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))
