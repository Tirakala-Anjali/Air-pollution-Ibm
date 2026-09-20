import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Filter, ChevronUp, ChevronDown } from 'lucide-react'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/EmptyState'
import SeverityBadge from '../components/SeverityBadge'
import DisclaimerBanner from '../components/DisclaimerBanner'
import { getEvents } from '../services/api'
import { formatTimestamp, formatDuration, formatValue } from '../utils/severity'

const SEVERITIES = ['ALL', 'SEVERE', 'HIGH', 'MODERATE', 'NORMAL']

function SortIcon({ col, sortKey, dir }) {
  if (sortKey !== col) return <span className="w-3 h-3 inline-block" />
  return dir === 'asc' ? <ChevronUp className="w-3 h-3 inline" /> : <ChevronDown className="w-3 h-3 inline" />
}

export default function Events() {
  const sessionId = sessionStorage.getItem('airguard_session')
  const navigate  = useNavigate()

  const [events,   setEvents]   = useState([])
  const [loading,  setLoading]  = useState(true)
  const [error,    setError]    = useState(null)
  const [filter,   setFilter]   = useState('ALL')
  const [sortKey,  setSortKey]  = useState('start_time')
  const [sortDir,  setSortDir]  = useState('desc')

  useEffect(() => {
    if (!sessionId) { setLoading(false); return }
    setLoading(true)
    getEvents(sessionId)
      .then(setEvents)
      .catch((e) => setError(e?.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [sessionId])

  if (!sessionId) return <EmptyState />
  if (loading)    return <LoadingSpinner message="Loading events…" />
  if (error)      return <ErrorMessage message={error} onRetry={() => window.location.reload()} />

  const filtered = filter === 'ALL' ? events : events.filter((e) => e.severity === filter)

  const sorted = [...filtered].sort((a, b) => {
    let av = a[sortKey], bv = b[sortKey]
    if (typeof av === 'string') av = av.toLowerCase()
    if (typeof bv === 'string') bv = bv.toLowerCase()
    if (av < bv) return sortDir === 'asc' ? -1 : 1
    if (av > bv) return sortDir === 'asc' ? 1  : -1
    return 0
  })

  const handleSort = (key) => {
    if (sortKey === key) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    else { setSortKey(key); setSortDir('asc') }
  }

  const cols = [
    { key: 'id',               label: '#'         },
    { key: 'start_time',       label: 'Start'     },
    { key: 'end_time',         label: 'End'       },
    { key: 'duration_minutes', label: 'Duration'  },
    { key: 'severity',         label: 'Severity'  },
    { key: 'max_pm25',         label: 'Max PM2.5' },
    { key: 'max_pm10',         label: 'Max PM10'  },
    { key: 'anomaly_score',    label: 'Avg Score' },
    { key: 'anomaly_count',    label: 'Records'   },
  ]

  return (
    <div className="space-y-5">
      <DisclaimerBanner />

      {/* Filter bar */}
      <div className="card flex flex-wrap items-center gap-3">
        <Filter className="w-4 h-4 text-slate-400" />
        <span className="text-xs text-slate-400">Filter by severity:</span>
        {SEVERITIES.map((s) => (
          <button
            key={s}
            onClick={() => setFilter(s)}
            className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors ${
              filter === s
                ? 'border-sky-500 bg-sky-500/20 text-sky-300'
                : 'border-slate-600 text-slate-400 hover:text-slate-200'
            }`}
          >
            {s === 'ALL' ? `All (${events.length})` : s}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="card overflow-x-auto">
        <h2 className="text-sm font-semibold text-white mb-4">
          Pollution Events
          <span className="ml-2 text-xs text-slate-400 font-normal">
            {sorted.length} event{sorted.length !== 1 ? 's' : ''}
          </span>
        </h2>

        {sorted.length === 0 ? (
          <p className="text-sm text-slate-400 text-center py-8">No events match the selected filter.</p>
        ) : (
          <table className="w-full text-xs">
            <thead>
              <tr className="text-slate-400 border-b border-slate-700">
                {cols.map((c) => (
                  <th
                    key={c.key}
                    className="text-left pb-2 pr-4 cursor-pointer select-none hover:text-slate-200 whitespace-nowrap"
                    onClick={() => handleSort(c.key)}
                  >
                    {c.label} <SortIcon col={c.key} sortKey={sortKey} dir={sortDir} />
                  </th>
                ))}
                <th className="text-left pb-2">Details</th>
              </tr>
            </thead>
            <tbody className="text-slate-300">
              {sorted.map((ev) => (
                <tr
                  key={ev.id}
                  className="border-b border-slate-700/40 hover:bg-slate-700/30 cursor-pointer"
                  onClick={() => navigate(`/events/${ev.id}`)}
                >
                  <td className="py-2.5 pr-4 font-mono text-slate-400">#{ev.id}</td>
                  <td className="py-2.5 pr-4 whitespace-nowrap">{formatTimestamp(ev.start_time)}</td>
                  <td className="py-2.5 pr-4 whitespace-nowrap">{formatTimestamp(ev.end_time)}</td>
                  <td className="py-2.5 pr-4">{formatDuration(ev.duration_minutes)}</td>
                  <td className="py-2.5 pr-4"><SeverityBadge severity={ev.severity} /></td>
                  <td className="py-2.5 pr-4">{formatValue(ev.max_pm25, ' µg/m³')}</td>
                  <td className="py-2.5 pr-4">{formatValue(ev.max_pm10, ' µg/m³')}</td>
                  <td className="py-2.5 pr-4">{ev.anomaly_score != null ? Number(ev.anomaly_score).toFixed(3) : '—'}</td>
                  <td className="py-2.5 pr-4">{ev.anomaly_count ?? '—'}</td>
                  <td className="py-2.5">
                    <span className="text-sky-400 hover:text-sky-300 text-xs">View →</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
