/**
 * Dashboard summary card.
 * Props: title, value, subtitle, icon (Lucide component), colorClass
 */
export default function StatCard({ title, value, subtitle, icon: Icon, colorClass = 'text-sky-400' }) {
  return (
    <div className="card flex items-start gap-4">
      {Icon && (
        <div className={`w-10 h-10 rounded-lg bg-slate-700/60 flex items-center justify-center shrink-0 ${colorClass}`}>
          <Icon className="w-5 h-5" />
        </div>
      )}
      <div className="min-w-0">
        <p className="text-xs text-slate-400 uppercase tracking-wide truncate">{title}</p>
        <p className="text-2xl font-bold text-white leading-tight mt-0.5">{value}</p>
        {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
      </div>
    </div>
  )
}
