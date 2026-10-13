import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


def _wrapped_lines(text: str, font: str, size: int, max_width: float):
    words = str(text).split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and stringWidth(candidate, font, size) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def generate_feasibility_report(data: dict, output_path: str):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 42
    content_width = width - margin * 2

    c.setFillColor(colors.HexColor("#1A365D"))
    c.rect(0, height - 92, width, 92, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(margin, height - 47, "AI ARSA ON FIZIBILITE RAPORU")
    c.setFont("Helvetica", 9)
    c.drawRightString(width - margin, height - 70, f"Tarih: {datetime.date.today().isoformat()}")

    y = height - 118

    def ensure_space(required=36):
        nonlocal y
        if y - required < 58:
            c.showPage()
            y = height - 55

    def heading(text):
        nonlocal y
        ensure_space(32)
        c.setFillColor(colors.HexColor("#1A365D"))
        c.setFont("Helvetica-Bold", 13)
        c.drawString(margin, y, text)
        y -= 22

    def line(label, value, color=colors.black):
        nonlocal y
        text = f"{label}: {value}"
        lines = _wrapped_lines(text, "Helvetica", 10, content_width - 10)
        ensure_space(14 * len(lines) + 4)
        c.setFillColor(color)
        c.setFont("Helvetica", 10)
        for item in lines:
            c.drawString(margin + 8, y, item)
            y -= 14
        y -= 2

    heading("1. Arsa ve konum")
    line("Lokasyon", data.get("location", "Belirtilmedi"))
    line("Arsa alani", f"{data.get('area_sqm', 0):,.2f} m2")
    line("Konum eslestirme", data.get("api_status", "Dogrulanmadi"))

    heading("2. Imar varsayimlari")
    zoning = data.get("zoning_info", {})
    line("Emsal / KAKS (varsayim)", zoning.get("emsal", "—"))
    line("TAKS (varsayim)", zoning.get("taks", "—"))
    line("Alan oranindan tahmini kat", zoning.get("max_kat", "—"))
    line("Not", zoning.get("note", "Resmi imar bilgisi degildir."))

    heading("3. Alan ve kapasite tahmini")
    capacity = data.get("capacity", {})
    line("Taban alani", f"{capacity.get('taban_alani_m2', 0):,.2f} m2")
    line("Toplam insaat alani", f"{capacity.get('toplam_insaat_alani_m2', 0):,.2f} m2")
    line("100 m2 bazinda tahmini daire", capacity.get("tahmini_daire_sayisi", "—"))

    heading("4. Finansal senaryo (canli fiyat degildir)")
    financials = data.get("financials", {})
    def money(value):
        return f"{float(value or 0):,.0f} TL".replace(",", ".")
    line("Tahmini insaat maliyeti", money(financials.get("toplam_maliyet_tl")))
    line("Tahmini satis geliri", money(financials.get("toplam_gelir_tl")))
    line("Tahmini fark (kar degildir)", money(financials.get("tahmini_kar_tl")), colors.HexColor("#2F855A"))

    concepts = data.get("concepts", [])
    if concepts:
        heading("5. Taslak konsept fikirleri")
        for concept in concepts:
            line("Fikir", concept)

    ensure_space(68)
    y -= 4
    c.setFillColor(colors.HexColor("#9B2C2C"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin, y, "ONEMLI SINIRLAMA")
    y -= 13
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#4A5568"))
    disclaimer = (
        "Bu belge otomatik on fizibilite prototipidir. Gorsel analiz edilmemis; resmi imar, "
        "parsel siniri, plan notu, ruhsat, maliyet veya piyasa fiyati dogrulanmamistir. "
        "Rakamlar kod icindeki varsayimlardan uretilmistir; yatirim veya ruhsat karari icin kullanmayin."
    )
    for item in _wrapped_lines(disclaimer, "Helvetica", 8, content_width):
        ensure_space(11)
        c.drawString(margin, y, item)
        y -= 11

    c.save()
