import { Upload } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function EmptyState({ message = 'No data yet. Upload a CSV to get started.' }) {
  return (
    <div className="flex flex-col items-center gap-4 py-16 text-center">
      <div className="w-14 h-14 rounded-full bg-slate-800 flex items-center justify-center">
        <Upload className="w-6 h-6 text-slate-500" />
      </div>
      <p className="text-slate-300 font-medium">No data loaded</p>
      <p className="text-sm text-slate-400 max-w-xs">{message}</p>
      <Link
        to="/upload"
        className="mt-1 px-5 py-2.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-white text-sm font-medium transition-colors"
      >
        Upload CSV
      </Link>
    </div>
  )
}
