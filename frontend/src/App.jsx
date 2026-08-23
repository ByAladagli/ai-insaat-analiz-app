import { useState } from 'react'
import axios from 'axios'
import { MapPin, Maximize2, Calculator, Building2, HardHat, FileText, Loader2, Download } from 'lucide-react'

function App() {
  const [file, setFile] = useState(null)
  const [location, setLocation] = useState('')
  const [area, setArea] = useState('')
  
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [preview, setPreview] = useState(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setPreview(URL.createObjectURL(e.target.files[0]))
    }
  }

  const handleAnalyze = async (e) => {
    e.preventDefault()
    if (!file || !location || !area) {
      setError("Lütfen arsa fotoğrafı, konum ve m² bilgisini eksiksiz girin.")
      return
    }

    setError(null)
    setLoading(true)

    const formData = new FormData()
    formData.append('image', file)
    formData.append('location', location)
    formData.append('area_sqm', area)

    try {
      const response = await axios.post('http://localhost:8000/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || "Analiz sırasında bir hata oluştu.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div 
      className="min-h-screen bg-slate-900 text-slate-50 p-6 flex flex-col items-center relative"
      style={{
        backgroundImage: "linear-gradient(to bottom, rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.95)), url('/architecture_bg.jpg')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed'
      }}
    >
      
      {/* Header */}
      <div className="w-full max-w-4xl flex items-center justify-between mb-12 relative z-10 mt-8">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl overflow-hidden shadow-[0_0_20px_rgba(245,158,11,0.5)] border-2 border-amber-500">
            <img src="/blueprint.jpg" alt="Logo" className="w-full h-full object-cover" />
          </div>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent drop-shadow-lg">
              AI İnşaat Analiz Motoru
            </h1>
            <p className="text-slate-300 font-medium">Arsa potansiyelinizi saniyeler içinde keşfedin</p>
          </div>
        </div>
      </div>

      <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-8 relative z-10">
        
        {/* Form Alanı */}
        <div className="bg-slate-900/70 p-6 rounded-2xl border border-slate-700 backdrop-blur-xl shadow-2xl">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <Calculator size={20} className="text-amber-500" />
            Arazi Bilgileri
          </h2>
          
          <form onSubmit={handleAnalyze} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Lokasyon</label>
              <div className="relative">
                <MapPin size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input 
                  type="text" 
                  value={location}
                  onChange={e => setLocation(e.target.value)}
                  placeholder="Örn: İstanbul, Kadıköy, Fikirtepe"
                  className="w-full bg-slate-950/60 border border-slate-700 rounded-lg py-3 pl-10 pr-4 text-slate-100 focus:outline-none focus:border-amber-500 transition-colors"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Toplam Arsa Alanı (m²)</label>
              <div className="relative">
                <Maximize2 size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input 
                  type="number" 
                  value={area}
                  onChange={e => setArea(e.target.value)}
                  placeholder="Örn: 1500"
                  className="w-full bg-slate-950/60 border border-slate-700 rounded-lg py-3 pl-10 pr-4 text-slate-100 focus:outline-none focus:border-amber-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Arsa / Harita Görseli</label>
              <label className="flex flex-col items-center justify-center w-full h-40 border-2 border-slate-700 border-dashed rounded-lg cursor-pointer bg-slate-950/60 hover:bg-slate-800 transition-all overflow-hidden relative group">
                {preview ? (
                  <>
                    <img src={preview} alt="Preview" className="absolute inset-0 w-full h-full object-cover opacity-70 group-hover:opacity-40 transition-opacity" />
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <span className="bg-slate-900/80 px-4 py-2 rounded-lg text-sm font-medium">Değiştirmek için tıkla</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="absolute inset-0 opacity-30 mix-blend-overlay" style={{backgroundImage: "url('/blueprint.jpg')", backgroundSize: 'cover', backgroundPosition: 'center'}}></div>
                    <div className="flex flex-col items-center justify-center pt-5 pb-6 relative z-10 bg-slate-900/60 p-4 rounded-xl backdrop-blur-sm">
                      <p className="text-sm text-slate-200">
                        <span className="font-semibold text-amber-500 text-lg">Tıklayın</span> veya görseli sürükleyin
                      </p>
                    </div>
                  </>
                )}
                <input type="file" className="hidden" accept="image/*" onChange={handleFileChange} />
              </label>
            </div>

            {error && <div className="text-red-400 text-sm bg-red-950/50 p-3 rounded-lg border border-red-500/50">{error}</div>}

            <button 
              type="submit" 
              disabled={loading}
              className="w-full py-4 bg-amber-500 hover:bg-amber-400 text-slate-900 rounded-lg font-bold shadow-[0_0_20px_rgba(245,158,11,0.4)] transition-all flex items-center justify-center gap-2 disabled:opacity-70 text-lg"
            >
              {loading ? (
                <><Loader2 size={24} className="animate-spin" /> Yapay Zeka Analiz Ediyor...</>
              ) : (
                <><Building2 size={24} /> Kapasiteyi Hesapla</>
              )}
            </button>
          </form>
        </div>

        {/* Sonuç Alanı */}
        <div className="bg-slate-900/70 p-6 rounded-2xl border border-slate-700 backdrop-blur-xl shadow-2xl relative overflow-hidden">
          {loading && (
            <div className="absolute inset-0 z-10 bg-slate-900/90 backdrop-blur-md flex flex-col items-center justify-center">
              <div className="w-20 h-20 border-4 border-slate-700 border-t-amber-500 rounded-full animate-spin mb-4"></div>
              <p className="text-amber-500 font-medium text-lg animate-pulse">İmar planları yapay zeka ile taranıyor...</p>
            </div>
          )}

          {!result && !loading && (
            <div className="h-full flex flex-col items-center justify-center text-slate-400">
              <div className="w-32 h-32 mb-6 opacity-30 rounded-full overflow-hidden border-2 border-slate-700">
                <img src="/blueprint.jpg" alt="No data" className="w-full h-full object-cover" />
              </div>
              <p className="text-lg">Analiz sonucu burada görüntülenecektir.</p>
            </div>
          )}

          {result && !loading && (
            <div className="h-full flex flex-col">
              <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 text-emerald-400">
                <FileText size={20} />
                Fizibilite Özeti
              </h2>
              
              <div className="space-y-4 flex-grow">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Hesaplanan Emsal</p>
                    <p className="text-2xl font-bold text-white">{result.data.zoning_info.emsal}</p>
                  </div>
                  <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-700">
                    <p className="text-xs text-slate-400 mb-1">Maksimum Kat</p>
                    <p className="text-2xl font-bold text-white">{result.data.zoning_info.max_kat}</p>
                  </div>
                </div>

                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-700">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-slate-400">Tahmini Daire (100m²)</span>
                    <span className="text-lg font-bold text-amber-500">{result.data.capacity.tahmini_daire_sayisi} Adet</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div className="bg-amber-500 h-2 rounded-full" style={{width: '75%'}}></div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-emerald-900/60 to-slate-950/80 p-5 rounded-xl border border-emerald-500/40">
                  <p className="text-sm text-emerald-400/80 mb-1">Tahmini Proje Kar Marjı</p>
                  <p className="text-3xl font-bold text-emerald-400 drop-shadow-[0_0_10px_rgba(52,211,153,0.3)]">
                    {new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY', maximumFractionDigits: 0 }).format(result.data.financials.tahmini_kar_tl)}
                  </p>
                </div>
              </div>

              <a 
                href={`http://localhost:8000${result.pdf_url}`}
                target="_blank"
                rel="noreferrer"
                className="mt-6 w-full py-4 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition-colors flex items-center justify-center gap-2 border border-slate-600 shadow-lg text-lg"
              >
                <Download size={24} />
                PDF Fizibilite Raporunu İndir
              </a>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}

export default App
