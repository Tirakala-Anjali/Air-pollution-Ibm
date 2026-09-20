import { ShieldAlert } from 'lucide-react'

export default function DisclaimerBanner() {
  return (
    <div className="flex gap-3 items-start bg-amber-950/40 border border-amber-800/60 rounded-lg p-3 text-xs text-amber-300">
      <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5" />
      <span>
        <strong>Responsible AI:</strong> AirGuard is a student educational project.
        Results are AI-generated statistical patterns and do <strong>not</strong> replace
        official government air-quality advisories or professional environmental assessments.
        Severity labels are custom categories, not official AQI classifications.
      </span>
    </div>
  )
}
