import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, CheckCircle, AlertCircle, FileText, Cpu, ChevronRight } from 'lucide-react'
import DisclaimerBanner from '../components/DisclaimerBanner'
import LoadingSpinner from '../components/LoadingSpinner'
import { uploadCSV, analyzeData, extractError } from '../services/api'

const STEPS = ['Select File', 'Preview Data', 'Run Analysis', 'View Results']

function StepIndicator({ current }) {
  return (
    <div className="flex items-center gap-2 mb-6 overflow-x-auto pb-1">
      {STEPS.map((label, i) => (
        <div key={label} className="flex items-center gap-2 shrink-0">
          <div className={`flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold border-2 ${
            i < current  ? 'bg-sky-500 border-sky-500 text-white'
            : i === current ? 'border-sky-400 text-sky-400'
            : 'border-slate-600 text-slate-500'
          }`}>
            {i < current ? '✓' : i + 1}
          </div>
          <span className={`text-xs ${i === current ? 'text-sky-300' : i < current ? 'text-slate-300' : 'text-slate-500'}`}>
            {label}
          </span>
          {i < STEPS.length - 1 && <ChevronRight className="w-3 h-3 text-slate-600" />}
        </div>
      ))}
    </div>
  )
}

export default function UploadData() {
  const navigate  = useNavigate()
  const fileRef   = useRef()

  const [step,         setStep]         = useState(0)
  const [file,         setFile]         = useState(null)
  const [uploadResult, setUploadResult] = useState(null)
  const [analysisResult, setAnalysisResult] = useState(null)
  const [contamination, setContamination]   = useState(0.05)
  const [loading,      setLoading]      = useState(false)
  const [error,        setError]        = useState(null)
  const [dragOver,     setDragOver]     = useState(false)

  /* ── Step 1: file selection ─────────────────────────────────────────────── */
  const handleFileSelect = (f) => {
    if (!f) return
    if (!f.name.toLowerCase().endsWith('.csv')) {
      setError('Only CSV files are supported.')
      return
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10 MB limit.')
      return
    }
    setError(null)
    setFile(f)
    handleUpload(f)
  }

  /* ── Step 2: upload & preview ───────────────────────────────────────────── */
  const handleUpload = async (f) => {
    setLoading(true)
    setError(null)
    try {
      const result = await uploadCSV(f)
      setUploadResult(result)
      setStep(1)
    } catch (e) {
      setError(extractError(e))
    } finally {
      setLoading(false)
    }
  }

  /* ── Step 3: run analysis ───────────────────────────────────────────────── */
  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    setStep(2)
    try {
      const result = await analyzeData(
        uploadResult.session_id,
        uploadResult._csv_b64,
        contamination
      )
      sessionStorage.setItem('airguard_session', uploadResult.session_id)
      setAnalysisResult(result)
      setStep(3)
    } catch (e) {
      setError(extractError(e))
      setStep(1)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl space-y-5">
      <DisclaimerBanner />
      <StepIndicator current={step} />

      {/* ── Step 0: drag-drop zone ────────────────────────────────────────── */}
      {step === 0 && (
        <div
          className={`card border-2 border-dashed text-center py-14 cursor-pointer transition-colors ${
            dragOver ? 'border-sky-400 bg-sky-500/10' : 'border-slate-600 hover:border-slate-500'
          }`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFileSelect(e.dataTransfer.files[0]) }}
          onClick={() => fileRef.current?.click()}
        >
          <input ref={fileRef} type="file" accept=".csv" className="hidden" onChange={(e) => handleFileSelect(e.target.files[0])} />
          {loading ? (
            <LoadingSpinner message="Uploading…" />
          ) : (
            <>
              <Upload className="w-10 h-10 mx-auto text-slate-500 mb-3" />
              <p className="text-slate-200 font-medium">Drag & drop a CSV file here</p>
              <p className="text-slate-500 text-sm mt-1">or click to browse · Max 10 MB</p>
            </>
          )}
          {error && (
            <div className="mt-4 flex items-center justify-center gap-2 text-red-400 text-sm">
              <AlertCircle className="w-4 h-4" /> {error}
            </div>
          )}
        </div>
      )}

      {/* ── Step 1: preview ──────────────────────────────────────────────── */}
      {step >= 1 && uploadResult && (
        <div className="card space-y-4">
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-sky-400" />
            <div>
              <p className="text-sm font-semibold text-white">{uploadResult.filename}</p>
              <p className="text-xs text-slate-400">{uploadResult.rows} rows · {uploadResult.columns.length} columns</p>
            </div>
          </div>

          <div>
            <p className="text-xs text-slate-400 mb-2">Detected columns:</p>
            <div className="flex flex-wrap gap-1.5">
              {uploadResult.columns.map((c) => (
                <span key={c} className="bg-slate-700 text-slate-300 text-xs px-2 py-0.5 rounded">{c}</span>
              ))}
            </div>
          </div>

          {/* Preview table */}
          {uploadResult.preview?.length > 0 && (
            <div>
              <p className="text-xs text-slate-400 mb-2">Data preview (first 10 rows):</p>
              <div className="overflow-x-auto rounded border border-slate-700">
                <table className="text-xs w-full">
                  <thead className="bg-slate-800">
                    <tr>
                      {Object.keys(uploadResult.preview[0]).map((k) => (
                        <th key={k} className="text-left px-3 py-2 text-slate-400 whitespace-nowrap">{k}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {uploadResult.preview.map((row, i) => (
                      <tr key={i} className="border-t border-slate-700/50 hover:bg-slate-700/20">
                        {Object.values(row).map((v, j) => (
                          <td key={j} className="px-3 py-1.5 text-slate-300 whitespace-nowrap">{String(v)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Contamination setting */}
          {step === 1 && (
            <div className="pt-2 border-t border-slate-700">
              <label className="text-xs text-slate-300 font-medium">
                Contamination Rate: <strong className="text-sky-400">{(contamination * 100).toFixed(0)}%</strong>
              </label>
              <p className="text-xs text-slate-500 mb-2">
                Expected fraction of anomalous records (1–20%). Default 5% is suitable for most datasets.
              </p>
              <input
                type="range" min={1} max={20} step={1}
                value={Math.round(contamination * 100)}
                onChange={(e) => setContamination(Number(e.target.value) / 100)}
                className="w-full accent-sky-500"
              />
            </div>
          )}

          {step === 1 && (
            <button
              onClick={handleAnalyze}
              className="w-full py-3 rounded-lg bg-sky-500 hover:bg-sky-400 text-white font-semibold text-sm flex items-center justify-center gap-2 transition-colors"
            >
              <Cpu className="w-4 h-4" /> Run AI Analysis
            </button>
          )}
          {error && <p className="text-red-400 text-sm text-center">{error}</p>}
        </div>
      )}

      {/* ── Step 2: analysing ────────────────────────────────────────────── */}
      {step === 2 && loading && (
        <div className="card text-center py-10">
          <div className="w-10 h-10 border-2 border-sky-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white font-medium">Running AI Analysis…</p>
          <p className="text-slate-400 text-sm mt-1">Preprocessing data → Isolation Forest → Event detection</p>
        </div>
      )}

      {/* ── Step 3: results ──────────────────────────────────────────────── */}
      {step === 3 && analysisResult && (
        <div className="card space-y-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-6 h-6 text-green-400" />
            <p className="text-white font-semibold">Analysis Complete</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {[
              { label: 'Records Processed',   value: analysisResult.preprocessing?.final_rows ?? '—' },
              { label: 'Anomalies Detected',  value: analysisResult.model_info?.anomalies_detected ?? '—' },
              { label: 'Events Found',        value: analysisResult.events_detected },
              { label: 'Anomaly Rate',        value: `${analysisResult.model_info?.anomaly_rate_pct ?? '—'}%` },
              { label: 'Features Used',       value: (analysisResult.model_info?.features_used ?? []).length },
              { label: 'Algorithm',           value: 'Isolation Forest' },
            ].map((item) => (
              <div key={item.label} className="bg-slate-700/50 rounded-lg p-3 text-center">
                <p className="text-xl font-bold text-sky-400">{item.value}</p>
                <p className="text-xs text-slate-400 mt-0.5">{item.label}</p>
              </div>
            ))}
          </div>

          {/* Preprocessing steps */}
          {analysisResult.preprocessing?.steps?.length > 0 && (
            <div className="bg-slate-800/60 rounded-lg p-3">
              <p className="text-xs font-medium text-slate-300 mb-2">Preprocessing steps applied:</p>
              <ul className="space-y-1">
                {analysisResult.preprocessing.steps.map((s, i) => (
                  <li key={i} className="text-xs text-slate-400 flex gap-2">
                    <span className="text-green-400">✓</span> {s}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              onClick={() => navigate('/')}
              className="flex-1 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-white font-semibold text-sm transition-colors"
            >
              View Dashboard
            </button>
            <button
              onClick={() => navigate('/events')}
              className="flex-1 py-2.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-200 font-semibold text-sm transition-colors"
            >
              View Events
            </button>
          </div>
        </div>
      )}

      {/* CSV format guide */}
      <div className="card text-xs text-slate-400 space-y-2">
        <p className="font-semibold text-slate-300">Expected CSV Format</p>
        <p>Required: a <strong className="text-slate-200">timestamp</strong> column and at least one pollutant column.</p>
        <p>Supported pollutants: <strong className="text-slate-200">pm25, pm10, no2, co, so2, o3</strong> (names are case-insensitive)</p>
        <p>Optional: temperature, humidity, wind_speed, location</p>
        <p>Timestamp formats: <code className="bg-slate-700 px-1 rounded">YYYY-MM-DD HH:MM:SS</code> or ISO 8601</p>
        <a href="/sample_air_quality.csv" className="text-sky-400 hover:underline" download>
          Download sample dataset →
        </a>
      </div>
    </div>
  )
}
