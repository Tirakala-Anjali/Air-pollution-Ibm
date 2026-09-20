import { useEffect, useState } from 'react'
import {
  ResponsiveContainer, ComposedChart, Area,
  XAxis, YAxis, Tooltip, Legend, CartesianGrid
} from 'recharts'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import EmptyState from '../components/EmptyState'
import DisclaimerBanner from '../components/DisclaimerBanner'
import { getTrends } from '../services/api'

const POLLUTANTS = [
  { key: 'pm25',  label: 'PM2.5',       unit: 'µg/m³', color: '#f87171' },
  { key: 'pm10',  label: 'PM10',        unit: 'µg/m³', color: '#fb923c' },
  { key: 'no2',   label: 'NO₂',         unit: 'µg/m³', color: '#fbbf24' },
  { key: 'co',    label: 'CO',          unit: 'mg/m³', color: '#a78bfa' },
  { key: 'so2',   label: 'SO₂',         unit: 'µg/m³', color: '#34d399' },
  { key: 'o3',    label: 'O₃ (Ozone)',  unit: 'µg/m³', color: '#38bdf8' },
  { key: 'temperature', label: 'Temperature', unit: '°C', color: '#f472b6' },
  { key: 'humidity',    label: 'Humidity',    unit: '%',  color: '#60a5fa' },
]

const CustomTooltip = ({ active, payload, label, unit }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  return (
    <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 text-xs shadow-xl">
      <p className="text-slate-300 mb-1">{new Date(label).toLocaleString('en-IN', { day:'2-digit', month:'short', hour:'2-digit', minute:'2-digit' })}</p>
      <p className="text-white font-semibold">{d?.value != null ? `${Number(d.value).toFixed(1)} ${unit}` : '—'}</p>
      {d?.is_anomaly && <p className="text-red-400 mt-1">⚠ Anomaly detected</p>}
      {d?.anomaly_score != null && <p className="text-slate-400">Score: {Number(d.anomaly_score).toFixed(3)}</p>}
    </div>
  )
}

/** Renders a red dot for anomaly points, invisible dot for normal points */
const AnomalyDot = (props) => {
  const { cx, cy, payload } = props
  if (!payload?.is_anomaly) return null
  return <circle cx={cx} cy={cy} r={5} fill="#f87171" stroke="#1e293b" strokeWidth={1.5} />
}

export default function Trends() {
  const sessionId = sessionStorage.getItem('airguard_session')
  const [selected, setSelected]   = useState('pm25')
  const [trendData, setTrendData] = useState(null)
  const [loading,   setLoading]   = useState(true)
  const [error,     setError]     = useState(null)

  useEffect(() => {
    if (!sessionId) { setLoading(false); return }
    setLoading(true)
    setError(null)
    getTrends(sessionId, selected)
      .then((d) => setTrendData(d))
      .catch((e) => setError(e?.response?.data?.detail || e.message))
      .finally(() => setLoading(false))
  }, [sessionId, selected])

  const pollutantCfg = POLLUTANTS.find((p) => p.key === selected) || POLLUTANTS[0]

  const chartData = (trendData?.data || []).map((pt) => ({
    timestamp:     pt.timestamp,
    value:         pt.value,
    is_anomaly:    pt.is_anomaly,
    anomaly_score: pt.anomaly_score,
  }))

  const xTickFormatter = (t) =>
    new Date(t).toLocaleString('en-IN', { month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit' })

  if (!sessionId) return <EmptyState />

  return (
    <div className="space-y-5">
      <DisclaimerBanner />

      {/* Pollutant selector */}
      <div className="card">
        <p className="text-xs text-slate-400 mb-3 uppercase tracking-wide">Select Pollutant</p>
        <div className="flex flex-wrap gap-2">
          {POLLUTANTS.map((p) => (
            <button
              key={p.key}
              onClick={() => setSelected(p.key)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                selected === p.key
                  ? 'border-sky-500 bg-sky-500/20 text-sky-300'
                  : 'border-slate-600 text-slate-400 hover:border-slate-500 hover:text-slate-200'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-white">
            {pollutantCfg.label} Time Series
          </h2>
          <span className="text-xs text-slate-400">
            {chartData.length} records · {chartData.filter((d) => d.is_anomaly).length} anomalies
          </span>
        </div>

        {loading ? (
          <LoadingSpinner message="Loading trend data…" />
        ) : error ? (
          <ErrorMessage message={error} onRetry={() => setSelected(selected)} />
        ) : chartData.length === 0 ? (
          <p className="text-slate-400 text-sm text-center py-10">No data available for this pollutant.</p>
        ) : (
          <ResponsiveContainer width="100%" height={340}>
            <ComposedChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={xTickFormatter}
                tick={{ fontSize: 10, fill: '#94a3b8' }}
                interval="preserveStartEnd"
              />
              <YAxis
                tick={{ fontSize: 10, fill: '#94a3b8' }}
                tickFormatter={(v) => v.toFixed(0)}
                unit={` ${pollutantCfg.unit}`}
                width={60}
              />
              <Tooltip content={<CustomTooltip unit={pollutantCfg.unit} />} />
              <Legend
                wrapperStyle={{ fontSize: 11, color: '#94a3b8' }}
              />

              {/* Area with custom anomaly dots */}
              <Area
                type="monotone"
                dataKey="value"
                name={`${pollutantCfg.label} (${pollutantCfg.unit})`}
                stroke={pollutantCfg.color}
                fill={pollutantCfg.color + '22'}
                strokeWidth={1.5}
                dot={<AnomalyDot />}
                activeDot={{ r: 4 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Legend explanation */}
      <div className="card text-xs text-slate-400 space-y-1">
        <p className="font-semibold text-slate-300">How to read this chart</p>
        <p>The coloured line shows the pollutant concentration over time.</p>
        <p>Red dots indicate records the Isolation Forest model flagged as anomalous relative to the dataset baseline.</p>
        <p>These are statistical anomalies – not official AQI exceedances.</p>
      </div>
    </div>
  )
}
