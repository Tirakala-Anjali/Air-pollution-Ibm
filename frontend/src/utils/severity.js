/**
 * Severity display helpers – colour classes, labels, icons.
 */

export const SEVERITY_CONFIG = {
  NORMAL:   { label: 'Normal',   badgeClass: 'badge-normal',   textClass: 'text-green-400',  dot: 'bg-green-400'  },
  MODERATE: { label: 'Moderate', badgeClass: 'badge-moderate', textClass: 'text-yellow-400', dot: 'bg-yellow-400' },
  HIGH:     { label: 'High',     badgeClass: 'badge-high',     textClass: 'text-orange-400', dot: 'bg-orange-400' },
  SEVERE:   { label: 'Severe',   badgeClass: 'badge-severe',   textClass: 'text-red-400',    dot: 'bg-red-400'    },
}

export const getSeverityConfig = (severity) =>
  SEVERITY_CONFIG[severity?.toUpperCase()] || SEVERITY_CONFIG.NORMAL

export const formatDuration = (minutes) => {
  if (!minutes && minutes !== 0) return '—'
  if (minutes < 60) return `${Math.round(minutes)} min`
  const h = Math.floor(minutes / 60)
  const m = Math.round(minutes % 60)
  return m ? `${h}h ${m}m` : `${h}h`
}

export const formatTimestamp = (ts) => {
  if (!ts) return '—'
  return new Date(ts).toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

export const formatValue = (val, unit = '') =>
  val != null ? `${Number(val).toFixed(1)}${unit}` : '—'
