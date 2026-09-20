import { Menu, Wind } from 'lucide-react'

export default function Topbar({ onMenuClick, title }) {
  return (
    <header className="sticky top-0 z-10 bg-slate-900/80 backdrop-blur border-b border-slate-700 px-4 py-3 flex items-center gap-3 lg:px-6">
      <button
        onClick={onMenuClick}
        className="lg:hidden p-1.5 rounded-md text-slate-400 hover:text-white hover:bg-slate-800"
        aria-label="Open navigation"
      >
        <Menu className="w-5 h-5" />
      </button>
      <h1 className="text-sm font-semibold text-white">{title}</h1>
    </header>
  )
}
