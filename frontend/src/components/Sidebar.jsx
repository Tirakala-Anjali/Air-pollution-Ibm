import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, TrendingUp, AlertTriangle,
  Upload, BookOpen, Info, Shield, MessageCircle, Wind
} from 'lucide-react'

const NAV_ITEMS = [
  { to: '/',          icon: LayoutDashboard, label: 'Dashboard'      },
  { to: '/trends',    icon: TrendingUp,      label: 'Pollution Trends'},
  { to: '/events',    icon: AlertTriangle,   label: 'Events'         },
  { to: '/upload',    icon: Upload,          label: 'Upload Data'    },
  { to: '/chat',      icon: MessageCircle,   label: 'AI Assistant'   },
  { to: '/awareness', icon: BookOpen,        label: 'Awareness'      },
  { to: '/responsible-ai', icon: Shield,     label: 'Responsible AI' },
  { to: '/about',     icon: Info,            label: 'About Project'  },
]

export default function Sidebar({ mobileOpen, onClose }) {
  return (
    <>
      {/* Backdrop on mobile */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside className={`
        fixed top-0 left-0 h-full w-64 z-30 flex flex-col
        bg-slate-900 border-r border-slate-700
        transform transition-transform duration-200
        ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:z-auto
      `}>
        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-700">
          <div className="w-9 h-9 rounded-lg bg-sky-500/20 flex items-center justify-center">
            <Wind className="w-5 h-5 text-sky-400" />
          </div>
          <div>
            <p className="font-bold text-white leading-tight">AirGuard</p>
            <p className="text-xs text-slate-400">AI Pollution Detection</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-sky-500/20 text-sky-400'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-4 py-3 border-t border-slate-700 text-xs text-slate-500">
          <p>1M1B × IBM SkillsBuild × AICTE</p>
          <p className="mt-0.5">SDG 11 · SDG 3 · SDG 13</p>
        </div>
      </aside>
    </>
  )
}
