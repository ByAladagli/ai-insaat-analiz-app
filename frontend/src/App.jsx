import { useEffect, useState } from 'react'
import axios from 'axios'
import { MapPin, Maximize2, Calculator, Building2, FileText, Loader2, Download, AlertTriangle } from 'lucide-react'

const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

function App() {
  const [file, setFile] = useState(null)
  const [location, setLocation] = useState('')
  const [area, setArea] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [preview, setPreview] = useState(null)

  useEffect(() => () => {
    if (preview) URL.revokeObjectURL(preview)
  }, [preview])

  const handleFileChange = (event) => {
    const nextFile = event.target.files?.[0]
    if (!nextFile) return
    if (nextFile.size > 10 * 1024 * 1024) {
      setError('Görsel en fazla 10 MB olabilir.')
      event.target.value = ''
      return
    }
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(nextFile.type)) {
      setError('JPG, PNG veya WebP formatında bir görsel seçin.')
      event.target.value = ''
      return
    }
    setError(null)
    setFile(nextFile)
    setPreview(URL.createObjectURL(nextFile))
  }

  const handleAnalyze = async (event) => {
    event.preventDefault()
    if (!file || !location.trim() || !area) {
      setError('Lütfen arsa görseli, konum ve m² bilgisini eksiksiz girin.')
      return
    }
    const areaValue = Number(area)
    if (!Number.isFinite(areaValue) || areaValue <= 0 || areaValue > 100000000) {
      setError('Arsa alanı 0 ile 100.000.000 m² arasında olmalıdır.')
      return
    }

    setError(null)
    setResult(null)
    setLoading(true)
    const formData = new FormData()
    formData.append('image', file)
    formData.append('location', location.trim())
    formData.append('area_sqm', String(areaValue))
    try {
      const response = await axios.post(`${API_BASE}/analyze`, formData, { timeout: 60000 })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Analiz tamamlanamadı. Backend servisinin çalıştığını kontrol edin.')
    } finally {
      setLoading(false)
    }
  }

  const money = (value) => new Intl.NumberFormat('tr-TR', {
    style: 'currency', currency: 'TRY', maximumFractionDigits: 0,
  }).format(value ?? 0)

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50 p-4 md:p-8 flex flex-col items-center"
      style={{ backgroundImage: "linear-gradient(to bottom, rgba(15,23,42,.88), rgba(15,23,42,.98)), url('/architecture_bg.jpg')", backgroundSize: 'cover', backgroundPosition: 'center' }}>
      <header className="w-full max-w-5xl flex items-center gap-4 my-6 md:my-10">
        <div className="w-14 h-14 rounded-xl overflow-hidden border border-amber-500 shrink-0">
          <img src="/blueprint.jpg" alt="AI İnşaat Analiz" className="w-full h-full object-cover" />
        </div>
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-amber-400">AI İnşaat Analiz Motoru</h1>
          <p className="text-slate-300">Arsa için yaklaşık ön fizibilite senaryosu</p>
        </div>
      </header>

      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 gap-6">
        <section className="bg-slate-900/80 p-5 md:p-6 rounded-2xl border border-slate-700 shadow-xl">
          <h2 className="text-lg font-semibold mb-5 flex items-center gap-2"><Calculator size={20} className="text-amber-400" /> Arazi Bilgileri</h2>
          <form onSubmit={handleAnalyze} className="space-y-5">
            <label className="block text-sm text-slate-300">
              Konum
              <span className="relative block mt-2">
                <MapPin size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input required maxLength={300} value={location} onChange={e => setLocation(e.target.value)}
                  placeholder="Örn: İstanbul, Kadıköy" className="w-full bg-slate-950 border border-slate-700 rounded-lg py-3 pl-10 pr-3 text-slate-100 focus:outline-none focus:border-amber-500" />
              </span>
            </label>
            <label className="block text-sm text-slate-300">
              Arsa alanı (m²)
              <span className="relative block mt-2">
                <Maximize2 size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input required type="number" min="0.01" max="100000000" step="any" value={area} onChange={e => setArea(e.target.value)}
                  placeholder="Örn: 1500" className="w-full bg-slate-950 border border-slate-700 rounded-lg py-3 pl-10 pr-3 text-slate-100 focus:outline-none focus:border-amber-500" />
              </span>
            </label>
            <div>
              <label className="block text-sm text-slate-300 mb-2">Arsa / harita görseli (JPG, PNG, WebP — en fazla 10 MB)</label>
              <label className="flex items-center justify-center w-full h-36 border-2 border-slate-700 border-dashed rounded-lg cursor-pointer bg-slate-950/70 hover:bg-slate-800 overflow-hidden relative">
                {preview ? <img src={preview} alt="Seçilen görsel önizlemesi" className="absolute inset-0 w-full h-full object-contain" /> :
                  <span className="text-amber-400">Görsel seçmek için tıklayın</span>}
                <input type="file" className="hidden" accept="image/jpeg,image/png,image/webp" onChange={handleFileChange} />
              </label>
            </div>
            {error && <div role="alert" className="text-red-300 text-sm bg-red-950/50 p-3 rounded-lg border border-red-500/50">{error}</div>}
            <button type="submit" disabled={loading} className="w-full py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-lg font-bold disabled:opacity-60 flex items-center justify-center gap-2">
              {loading ? <><Loader2 size={20} className="animate-spin" /> Ön fizibilite hesaplanıyor...</> : <><Building2 size={20} /> Ön Fizibilite Oluştur</>}
            </button>
          </form>
        </section>

        <section className="bg-slate-900/80 p-5 md:p-6 rounded-2xl border border-slate-700 shadow-xl min-h-96">
          {!result && !loading && <div className="h-full min-h-64 flex flex-col items-center justify-center text-center text-slate-400">
            <FileText size={42} className="mb-4 opacity-60" />
            <p>Analiz sonucu burada görüntülenecektir.</p>
          </div>}
          {loading && <div className="h-full min-h-64 flex flex-col items-center justify-center text-amber-400">
            <Loader2 size={36} className="animate-spin mb-4" />
            <p>Yaklaşık alan ve maliyet senaryosu hazırlanıyor...</p>
          </div>}
          {result && !loading && <>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-emerald-400"><FileText size={20} /> Ön Fizibilite Özeti</h2>
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-700"><p className="text-xs text-slate-400">Emsal varsayımı</p><p className="text-2xl font-bold">{result.data.zoning_info.emsal}</p></div>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-700"><p className="text-xs text-slate-400">Alan oranından tahmini kat</p><p className="text-2xl font-bold">{result.data.zoning_info.max_kat}</p></div>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-700 col-span-2"><p className="text-xs text-slate-400">100 m² bazında tahmini daire</p><p className="text-xl font-bold text-amber-400">{result.data.capacity.tahmini_daire_sayisi}</p></div>
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-700 col-span-2"><p className="text-xs text-slate-400">Tahmini gelir-gider farkı (resmî kâr değildir)</p><p className="text-2xl font-bold text-emerald-400">{money(result.data.financials.tahmini_kar_tl)}</p></div>
            </div>
            <div className="rounded-xl border border-amber-500/50 bg-amber-950/30 p-3 mb-4 text-sm text-amber-100">
              <p className="font-semibold flex gap-2 items-center mb-1"><AlertTriangle size={16} /> Önemli sınırlama</p>
              <p>{result.data.report_notice || 'Değerler yaklaşık varsayımlardır; resmî imar veya piyasa verisi değildir.'}</p>
              <p className="mt-2">Görsel analizi: yapılmadı. Emsal, TAKS ve fiyatlar resmî/canlı kaynaklardan doğrulanmıyor.</p>
            </div>
            <a href={`${API_BASE}${result.pdf_url}`} target="_blank" rel="noreferrer"
              className="w-full py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium flex items-center justify-center gap-2 border border-slate-600">
              <Download size={20} /> PDF Ön Fizibilite Raporunu İndir
            </a>
          </>}
        </section>
      </div>
    </main>
  )
}

export default App
