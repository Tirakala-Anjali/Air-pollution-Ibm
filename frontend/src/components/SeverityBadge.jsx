import { getSeverityConfig } from '../utils/severity'

export default function SeverityBadge({ severity }) {
  const cfg = getSeverityConfig(severity)
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold ${cfg.badgeClass}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  )
}
