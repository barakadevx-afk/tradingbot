import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  ArrowLeftRight,
  Briefcase,
  BarChart3,
  Brain,
  Settings,
  Bot,
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/trading', icon: ArrowLeftRight, label: 'Trading' },
  { to: '/portfolio', icon: Briefcase, label: 'Portfolio' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/ai-insights', icon: Brain, label: 'AI Insights' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-6 border-b border-surface-700/50">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-glow-primary">
          <Bot className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-surface-100">BARAKA AI</h1>
          <p className="text-xs text-surface-500">Trading Platform</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `nav-link ${isActive ? 'nav-link-active' : ''}`
            }
          >
            <item.icon className="w-5 h-5" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom section */}
      <div className="px-4 py-4 border-t border-surface-700/50">
        <div className="glass-card-sm p-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-primary-500 pulse-dot" />
            <span className="text-xs font-medium text-primary-400">AI Active</span>
          </div>
          <p className="text-xs text-surface-500">
            Model v2.4.1 running
          </p>
        </div>
      </div>
    </aside>
  )
}
