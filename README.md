# AI İnşaat Analiz Uygulaması

React/Vite arayüzü ve FastAPI tabanlı bir **ön fizibilite prototipi**. Resmî imar sorgusu, parsel ölçümü veya görselden yapay zekâ ile analiz henüz entegre değildir. Maliyet, satış ve emsal değerleri kod içindeki örnek varsayımlardır; yatırım/ruhsat kararı için kullanılmamalıdır.

## Gereksinimler
- Python 3.10+
- Node.js 20+
- Git

## Backend (Windows PowerShell)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:NOMINATIM_USER_AGENT = "AIInsaatAnalizApp/1.1 (contact: your-email@example.com)"
uvicorn main:app --host 127.0.0.1 --port 8000
```
Health check: http://127.0.0.1:8000/health

Nominatim isteği, yalnızca `NOMINATIM_USER_AGENT` tanımlanırsa gönderilir. Değer olarak kendi uygulama tanımınızı ve iletişim adresinizi girin; örnek adresi aynen kullanmayın.

## Frontend
```powershell
cd frontend
npm ci
npm run dev
```
Vite geliştirme sunucusu varsayılan olarak http://localhost:5173 adresinde açılır. Uygulama API'si varsayılan olarak http://127.0.0.1:8000 kullanır.

## Güvenlik ve sınırlamalar
- Görsel yükleme 10 MB ile sınırlıdır; uzantı ile dosya imzası kontrol edilir.
- Dosya adları sunucu tarafından üretilir; istemcinin dosya adı yol olarak kullanılmaz.
- CORS varsayılan olarak yalnızca yerel Vite adreslerine açıktır. Başka bir frontend adresi için `CORS_ALLOWED_ORIGINS` ortam değişkenini virgülle ayrılmış origin listesi olarak tanımlayın.
- PDF raporları `backend/reports` altında tutulur. Üretim ortamına açmadan önce kimlik doğrulama, rapor erişim yetkilendirmesi, otomatik saklama süresi ve oran sınırlaması ekleyin.
- Yüklenen görsel şu an bir vision modeline gönderilmiyor; `image_analysis_status=not_performed` döndürülür.
- Emsal, TAKS, maliyet ve satış değerleri gerçek zamanlı/resmî değildir. Geocoding yalnızca konumu eşleştirir; imar hakkını doğrulamaz.

## Geliştirme kontrolleri
```powershell
python -m compileall backend
cd frontend
npm ci
npm run build
npm run lint
```
