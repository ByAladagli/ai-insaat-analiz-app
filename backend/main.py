from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
import os
import shutil

from ai_engine import analyze_land
from pdf_generator import generate_feasibility_report

app = FastAPI(title="AI Insaat Analiz API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/analyze")
async def process_land(
    image: UploadFile = File(...),
    location: str = Form(...),
    area_sqm: float = Form(...)
):
    # 1. Girdi Güvenliği: Dosya uzantısı kontrolü
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    ext = os.path.splitext(image.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Sadece resim dosyaları yükleyebilirsiniz (JPG, PNG).")

    # Dosyayı gecici olarak kaydet
    file_path = os.path.join(UPLOAD_DIR, image.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
            
        # 2. AI Analiz Motorunu Çağır (TAKS, KAKS hesabı vs.)
        analysis_result = await analyze_land(file_path, location, area_sqm)
        
        # 3. PDF Rapor Üretimi
        pdf_path = os.path.join(UPLOAD_DIR, f"rapor_{image.filename}.pdf")
        generate_feasibility_report(analysis_result, pdf_path)
        
        # Sonucu Dön
        return JSONResponse(content={
            "success": True,
            "data": analysis_result,
            "pdf_url": f"/download-report/{os.path.basename(pdf_path)}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analiz sırasında hata oluştu: {str(e)}")
    finally:
        # Resim sunucuda gereksiz yer kaplamasın (Gizlilik ve Performans)
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/download-report/{filename}")
async def download_report(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Rapor bulunamadı.")
    return FileResponse(file_path, media_type="application/pdf", filename="Fizibilite_Raporu.pdf")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
