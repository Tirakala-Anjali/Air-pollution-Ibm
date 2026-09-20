import { useEffect, useState, useCallback } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  Database, AlertTriangle, TrendingUp, Wind,
  Activity, BarChart2, Zap, FlaskConical, Upload, Cpu
} from 'lucide-react'
import StatCard from '../components/StatCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import SeverityBadge from '../components/SeverityBadge'
import DisclaimerBanner from '../components/DisclaimerBanner'
import { getDashboard, getEvents, loadDemo, extractError } from '../services/api'
import { formatTimestamp, formatDuration, formatValue } from '../utils/severity'

/* ── Demo landing card shown when no session is active ─────────────────────── */
function DemoLanding({ onLoadDemo, loading, error }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-6 max-w-lg mx-auto text-center">
      {/* Icon */}
      <div className="w-16 h-16 rounded-2xl bg-sky-500/15 flex items-center justify-center">
        <Wind className="w-8 h-8 text-sky-400" />
      </div>

      {/* Heading */}
      <div className="space-y-2">
        <h2 className="text-xl font-bold text-white">Welcome to AirGuard</h2>
        <p className="text-sm text-slate-400 leading-relaxed">
          AI-based air pollution event detection using Isolation Forest.
          Load the included synthetic demo dataset to see a full analysis instantly,
          or upload your own CSV data.
        </p>
      </div>

      {/* Primary action — Load Demo Data */}
      <div className="w-full space-y-3">
        <button
          onClick={onLoadDemo}
          disabled={loading}
          className="w-full flex items-center justify-center gap-3 py-4 rounded-xl
                     bg-sky-500 hover:bg-sky-400 disabled:opacity-60 disabled:cursor-not-allowed
                     text-white font-semibold text-sm transition-colors shadow-lg shadow-sky-500/20"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
              Running AI Analysis…
            </>
          ) : (
            <>
              <FlaskConical className="w-4 h-4" />
              Load Demo Data
            </>
          )}
        </button>

        {/* What happens when they click */}
        {!loading && (
          <div className="bg-slate-800/60 rounded-lg px-4 py-3 text-left space-y-1.5">
            <p className="text-xs font-semibold text-slate-300">What this does:</p>
            {[
              'Loads the included synthetic demo dataset (96 hourly records)',
              'Runs the Isolation Forest anomaly detection model',
              'Groups consecutive anomalies into pollution events',
              'Classifies severity and generates AI explanations',
              'Displays all results on this dashboard',
            ].map((step, i) => (
              <p key={i} className="text-xs text-slate-400 flex gap-2">
                <span className="text-sky-400 shrink-0">→</span>{step}
              </p>
            ))}
            <p className="text-xs text-amber-400/80 mt-2 pt-2 border-t border-slate-700">
              ⚠ Synthetic Demo Data — not real-world measurements
            </p>
          </div>
        )}
      </div>

      {/* Loading progress indicator */}
      {loading && (
        <div className="w-full bg-slate-800 rounded-lg p-4 text-left space-y-2">
          <p className="text-xs font-semibold text-slate-300 flex items-center gap-2">
            <Cpu className="w-3.5 h-3.5 text-sky-400" />
            Processing pipeline…
          </p>
          {[
            'Loading synthetic demo dataset',
            'Preprocessing — column mapping, deduplication',
            'Running Isolation Forest (200 trees)',
            'Grouping anomalies into pollution events',
            'Generating AI explanations',
          ].map((step, i) => (
            <p key={i} className="text-xs text-slate-400 flex gap-2">
              <span className="text-sky-400 animate-pulse">•</span>{step}
            </p>
          ))}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="w-full bg-red-950/40 border border-red-800/60 rounded-lg px-4 py-3 text-xs text-red-300">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Divider */}
      <div className="w-full flex items-center gap-3">
        <div className="flex-1 h-px bg-slate-700" />
        <span className="text-xs text-slate-500">or</span>
        <div className="flex-1 h-px bg-slate-700" />
      </div>

      {/* Secondary action — Upload own data */}
      <Link
        to="/upload"
        className="w-full flex items-center justify-center gap-2 py-3 rounded-xl
                   border border-slate-600 hover:border-slate-500 hover:bg-slate-800
                   text-slate-300 text-sm font-medium transition-colors"
      >
        <Upload className="w-4 h-4" />
        Upload your own CSV dataset
      </Link>
    </div>
  )
}

/* ── Main Dashboard ─────────────────────────────────────────────────────────── */
export default function Dashboard() {
  const navigate = useNavigate()

  // Session lives in sessionStorage so navigation keeps it alive
  const [sessionId, setSessionId] = useState(
    () => sessionStorage.getItem('airguard_session') || null
  )

  const [stats,       setStats]       = useState(null)
  const [events,      setEvents]      = useState([])
  const [loading,     setLoading]     = useState(!!sessionId)   // only show spinner if session exists
  const [demoLoading, setDemoLoading] = useState(false)
  const [demoError,   setDemoError]   = useState(null)
  const [error,       setError]       = useState(null)
  const [isDemo,      setIsDemo]      = useState(
    () => sessionStorage.getItem('airguard_is_demo') === 'true'
  )

  /* fetch dashboard + events whenever sessionId changes */
  const fetchDashboard = useCallback((sid) => {
    if (!sid) return
    setLoading(true)
    setError(null)
    Promise.all([getDashboard(sid), getEvents(sid)])
      .then(([s, e]) => { setStats(s); setEvents(e) })
      .catch((err) => setError(err?.response?.data?.detail || err.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    fetchDashboard(sessionId)
  }, [sessionId, fetchDashboard])

  /* ── Load Demo Data handler ────────────────────────────────────────────── */
  const handleLoadDemo = async () => {
    setDemoLoading(true)
    setDemoError(null)
    try {
      const result = await loadDemo()
      // Persist session exactly like the Upload page does
      sessionStorage.setItem('airguard_session', result.session_id)
      sessionStorage.setItem('airguard_is_demo', 'true')
      setIsDemo(true)
      setSessionId(result.session_id)
      // fetchDashboard is triggered by the sessionId state change above
    } catch (err) {
      setDemoError(extractError(err))
      setDemoLoading(false)
    }
  }

  /* ── Render ────────────────────────────────────────────────────────────── */
  if (loading || (demoLoading && !stats)) {
    return <LoadingSpinner message={demoLoading ? 'Running AI analysis on demo data…' : 'Loading dashboard…'} />
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={() => fetchDashboard(sessionId)} />
  }

  /* No session yet — show the demo landing card */
  if (!sessionId || !stats) {
    return (
      <DemoLanding
        onLoadDemo={handleLoadDemo}
        loading={demoLoading}
        error={demoError}
      />
    )
  }

  /* ── Dashboard with real data ─────────────────────────────────────────── */
  const recentEvents = [...events]
    .sort((a, b) => new Date(b.start_time) - new Date(a.start_time))
    .slice(0, 5)

  return (
    <div className="space-y-6">
      <DisclaimerBanner />

      {/* Demo dataset notice */}
      {isDemo && (
        <div className="flex items-center justify-between gap-3 bg-sky-950/50 border border-sky-800/60 rounded-lg px-4 py-2.5">
          <div className="flex items-center gap-2 text-xs text-sky-300">
            <FlaskConical className="w-3.5 h-3.5 shrink-0" />
            <span>
              <strong>Synthetic Demo Data</strong> — These results are generated from the
              included sample dataset and do not represent real-world measurements.
            </span>
          </div>
          <Link
            to="/upload"
            className="shrink-0 text-xs text-sky-400 hover:text-sky-300 underline underline-offset-2"
          >
            Upload real data →
          </Link>
        </div>
      )}

      {/* Stat cards — row 1 */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Records"
          value={stats.total_records.toLocaleString()}
          icon={Database}
          colorClass="text-sky-400"
          subtitle={`${stats.date_range?.start?.slice(0,10)} – ${stats.date_range?.end?.slice(0,10)}`}
        />
        <StatCard
          title="Events Detected"
          value={stats.events_detected}
          icon={AlertTriangle}
          colorClass="text-orange-400"
          subtitle={`${stats.high_severity} high/severe`}
        />
        <StatCard
          title="Anomaly Rate"
          value={`${stats.anomaly_rate_pct}%`}
          icon={Activity}
          colorClass="text-purple-400"
          subtitle="of all measurements"
        />
        <StatCard
          title="Current Status"
          value={stats.current_status}
          icon={Zap}
          colorClass={stats.current_status === 'NORMAL' ? 'text-green-400' : 'text-red-400'}
          subtitle="most recent event"
        />
      </div>

      {/* Stat cards — row 2 */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Highest PM2.5"
          value={formatValue(stats.highest_pm25, ' µg/m³')}
          icon={Wind}
          colorClass="text-red-400"
          subtitle="peak during period"
        />
        <StatCard
          title="Highest PM10"
          value={formatValue(stats.highest_pm10, ' µg/m³')}
          icon={BarChart2}
          colorClass="text-orange-400"
          subtitle="peak during period"
        />
        <StatCard
          title="Avg PM2.5"
          value={formatValue(stats.avg_pm25, ' µg/m³')}
          icon={TrendingUp}
          colorClass="text-sky-400"
          subtitle="mean for period"
        />
        <StatCard
          title="High Severity Events"
          value={stats.high_severity}
          icon={AlertTriangle}
          colorClass="text-red-400"
          subtitle="HIGH or SEVERE"
        />
      </div>

      {/* AI model info */}
      <div className="card">
        <h2 className="text-sm font-semibold text-white mb-3">AI Model Information</h2>
        <div className="flex flex-wrap gap-4 text-xs text-slate-400">
          <span className="bg-slate-700 rounded px-2 py-1">
            Algorithm: <strong className="text-slate-200">Isolation Forest</strong>
          </span>
          <span className="bg-slate-700 rounded px-2 py-1">
            Type: <strong className="text-slate-200">Unsupervised</strong>
          </span>
          <span className="bg-slate-700 rounded px-2 py-1">
            Features: <strong className="text-slate-200">PM2.5, PM10, NO₂, CO, SO₂, O₃</strong>
          </span>
          <span className="bg-slate-700 rounded px-2 py-1">
            Scores: <strong className="text-slate-200">Relative (0–1)</strong>
          </span>
        </div>
      </div>

      {/* Recent events */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-white">Recent Pollution Events</h2>
          <button
            onClick={() => navigate('/events')}
            className="text-xs text-sky-400 hover:text-sky-300"
          >
            View all →
          </button>
        </div>

        {recentEvents.length === 0 ? (
          <p className="text-sm text-slate-400 py-4 text-center">No pollution events detected.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-slate-400 border-b border-slate-700">
                  <th className="text-left pb-2 pr-4">ID</th>
                  <th className="text-left pb-2 pr-4">Start Time</th>
                  <th className="text-left pb-2 pr-4">Duration</th>
                  <th className="text-left pb-2 pr-4">Severity</th>
                  <th className="text-right pb-2">Max PM2.5</th>
                </tr>
              </thead>
              <tbody className="text-slate-300">
                {recentEvents.map((ev) => (
                  <tr
                    key={ev.id}
                    className="border-b border-slate-700/50 hover:bg-slate-700/30 cursor-pointer"
                    onClick={() => navigate(`/events/${ev.id}`)}
                  >
                    <td className="py-2 pr-4 font-mono">#{ev.id}</td>
                    <td className="py-2 pr-4">{formatTimestamp(ev.start_time)}</td>
                    <td className="py-2 pr-4">{formatDuration(ev.duration_minutes)}</td>
                    <td className="py-2 pr-4"><SeverityBadge severity={ev.severity} /></td>
                    <td className="py-2 text-right">{formatValue(ev.max_pm25, ' µg/m³')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Reload demo / switch dataset */}
      <div className="flex flex-wrap gap-3 pb-2">
        <button
          onClick={handleLoadDemo}
          disabled={demoLoading}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600
                     text-slate-300 text-xs font-medium transition-colors disabled:opacity-50"
        >
          <FlaskConical className="w-3.5 h-3.5" />
          {demoLoading ? 'Reloading…' : 'Reload Demo Data'}
        </button>
        <Link
          to="/upload"
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-600
                     hover:bg-slate-800 text-slate-400 text-xs font-medium transition-colors"
        >
          <Upload className="w-3.5 h-3.5" />
          Upload your own data
        </Link>
      </div>
    </div>
  )
}
