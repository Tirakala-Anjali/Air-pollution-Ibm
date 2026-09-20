import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Clock, Activity, Wind, AlertTriangle } from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import SeverityBadge from '../components/SeverityBadge'
import DisclaimerBanner from '../components/DisclaimerBanner'
import { getEventById } from '../services/api'
import { formatTimestamp, formatDuration, formatValue, getSeverityConfig } from '../utils/severity'

function MetaRow({ label, value }) {
  return (
    <div className="flex justify-between py-2 border-b border-slate-700/50 text-sm">
      <span className="text-slate-400">{label}</span>
      <span className="text-slate-200 font-medium">{value}</span>
    </div>
  )
}

function PollutantBar({ label, value, max, unit, color }) {
  const pct = max && value != null ? Math.min((value / max) * 100, 100) : 0
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span className="text-slate-200">{value != null ? `${Number(value).toFixed(1)} ${unit}` : '—'}</span>
      </div>
      <div className="h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

export default function EventDetail() {
  const { id }     = useParams()
  const navigate   = useNavigate()
  const sessionId  = sessionStorage.getItem('airguard_session')

  const [event,   setEvent]   = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  useEffect(() => {
    if (!sessionId) { setLoading(false); return }
    getEventById(id, sessionId)
      .then(setEvent)
      .catch((e) => setError(e?.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [id, sessionId])

  if (loading) return <LoadingSpinner message="Loading event details…" />
  if (error)   return <ErrorMessage message={error} />
  if (!event)  return <ErrorMessage message="Event not found." />

  const cfg = getSeverityConfig(event.severity)
  const maxPollutant = Math.max(event.max_pm25 ?? 0, event.max_pm10 ?? 0, 1)

  return (
    <div className="space-y-5 max-w-4xl">
      {/* Back button */}
      <button
        onClick={() => navigate('/events')}
        className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Events
      </button>

      {/* Header card */}
      <div className="card">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs text-slate-400 mb-1">Pollution Event #{event.id}</p>
            <h1 className="text-xl font-bold text-white">
              {event.severity} Pollution Event
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              {formatTimestamp(event.start_time)} → {formatTimestamp(event.end_time)}
            </p>
          </div>
          <SeverityBadge severity={event.severity} />
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-5">
        {/* Event metadata */}
        <div className="card space-y-0">
          <h2 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Clock className="w-4 h-4 text-sky-400" /> Event Summary
          </h2>
          <MetaRow label="Start Time"       value={formatTimestamp(event.start_time)} />
          <MetaRow label="End Time"         value={formatTimestamp(event.end_time)} />
          <MetaRow label="Duration"         value={formatDuration(event.duration_minutes)} />
          <MetaRow label="Anomalous Records" value={`${event.anomaly_count ?? '—'} observations`} />
          <MetaRow label="Avg Anomaly Score" value={event.anomaly_score != null ? Number(event.anomaly_score).toFixed(4) : '—'} />
          <MetaRow label="Severity"         value={<SeverityBadge severity={event.severity} />} />
        </div>

        {/* Peak pollutant values */}
        <div className="card">
          <h2 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
            <Wind className="w-4 h-4 text-sky-400" /> Peak Pollutant Values
          </h2>
          <div className="space-y-3">
            <PollutantBar label="PM2.5"  value={event.max_pm25} max={300} unit="µg/m³" color="bg-red-500" />
            <PollutantBar label="PM10"   value={event.max_pm10} max={500} unit="µg/m³" color="bg-orange-500" />
            <PollutantBar label="NO₂"    value={event.max_no2}  max={200} unit="µg/m³" color="bg-yellow-500" />
            <PollutantBar label="CO"     value={event.max_co}   max={10}  unit="mg/m³" color="bg-purple-500" />
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2 text-xs">
            <div className="bg-slate-700/50 rounded p-2">
              <p className="text-slate-400">Avg PM2.5</p>
              <p className="text-white font-semibold">{formatValue(event.avg_pm25, ' µg/m³')}</p>
            </div>
            <div className="bg-slate-700/50 rounded p-2">
              <p className="text-slate-400">Avg PM10</p>
              <p className="text-white font-semibold">{formatValue(event.avg_pm10, ' µg/m³')}</p>
            </div>
          </div>
        </div>
      </div>

      {/* AI Explanation */}
      {event.explanation && (
        <div className="card border-l-4 border-sky-500">
          <h2 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <Activity className="w-4 h-4 text-sky-400" /> AI-Generated Explanation
          </h2>
          <div className="space-y-3">
            {event.explanation.split('\n\n').map((para, i) => (
              <p
                key={i}
                className={`text-sm leading-relaxed ${
                  para.startsWith('⚠️') ? 'text-amber-300 bg-amber-950/30 border border-amber-800/40 rounded p-3' : 'text-slate-300'
                }`}
              >
                {para}
              </p>
            ))}
          </div>
        </div>
      )}

      <DisclaimerBanner />
    </div>
  )
}
