from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import datetime

def generate_feasibility_report(data: dict, output_path: str):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    
    # Başlık ve Tasarım
    c.setFillColor(colors.HexColor("#1A365D")) # Koyu mavi kurumsal renk
    c.rect(0, height - 100, width, 100, fill=1, stroke=0)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(40, height - 60, "AI ARSA FIZIBILITE RAPORU")
    
    c.setFont("Helvetica", 10)
    c.drawString(width - 150, height - 60, f"Tarih: {datetime.date.today()}")
    
    # İçerik Alanı
    c.setFillColor(colors.black)
    
    y = height - 150
    
    # Arsa ve İmar Bilgileri
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "1. Arsa ve Imar Analizi")
    y -= 30
    
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Lokasyon: {data['location']}")
    y -= 20
    c.drawString(50, y, f"Arsa Alani: {data['area_sqm']} m2")
    y -= 20
    c.drawString(50, y, f"Emsal (KAKS): {data['zoning_info']['emsal']}")
    y -= 20
    c.drawString(50, y, f"TAKS: {data['zoning_info']['taks']}")
    y -= 20
    c.drawString(50, y, f"Maksimum Kat: {data['zoning_info']['max_kat']} Kat")
    y -= 40
    
    # Kapasite
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "2. Yapi Kapasitesi")
    y -= 30
    
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Taban Alani: {data['capacity']['taban_alani_m2']} m2")
    y -= 20
    c.drawString(50, y, f"Toplam Insaat Alani: {data['capacity']['toplam_insaat_alani_m2']} m2")
    y -= 20
    c.drawString(50, y, f"Tahmini Daire Sayisi (100m2): {data['capacity']['tahmini_daire_sayisi']} Adet")
    y -= 40
    
    # Finansal
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "3. Tahmini Maliyet & Finansal Rapor")
    y -= 30
    
    def format_money(val):
        return f"{val:,.0f} TL".replace(",", ".")
        
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Tahmini Insaat Maliyeti: {format_money(data['financials']['toplam_maliyet_tl'])}")
    y -= 20
    c.drawString(50, y, f"Tahmini Satis Geliri: {format_money(data['financials']['toplam_gelir_tl'])}")
    y -= 20
    
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#2F855A")) # Yeşil
    c.drawString(50, y, f"Olası Kar Marji: {format_money(data['financials']['tahmini_kar_tl'])}")
    c.setFillColor(colors.black)
    y -= 40
    
    # Konseptler
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "4. Yapay Zeka Konsept Onerileri")
    y -= 30
    
    c.setFont("Helvetica", 12)
    for concept in data['concepts']:
        c.drawString(50, y, f"- {concept}")
        y -= 20
        
    # Alt bilgi
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.gray)
    c.drawString(40, 40, "Bu rapor AI Insaat Analiz Motoru tarafindan uretilmistir. Degerler yaklasik ve simulasyondur.")

    c.save()
