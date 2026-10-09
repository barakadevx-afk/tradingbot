import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ArrowLeftRight,
  Briefcase,
  BarChart3,
  Brain,
  Settings,
  Shield,
  Menu,
  X,
  Activity,
  Bell,
  Plug,
  BookOpen,
  Users,
  ScrollText,
  History,
  FlaskConical,
  Layers,
  Cpu,
  Radar,
} from 'lucide-react';

const tradingNav = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/trading', icon: ArrowLeftRight, label: 'Trading' },
  { to: '/signals', icon: Brain, label: 'AI Signals' },
  { to: '/portfolio', icon: Briefcase, label: 'Portfolio' },
  { to: '/positions', icon: Activity, label: 'Positions' },
  { to: '/orders', icon: History, label: 'Orders' },
  { to: '/trades', icon: ScrollText, label: 'Trade History' },
];

const analysisNav = [
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/backtesting', icon: FlaskConical, label: 'Backtesting' },
  { to: '/scanner', icon: Radar, label: 'Market Scanner' },
  { to: '/strategies', icon: Layers, label: 'Strategies' },
  { to: '/models', icon: Cpu, label: 'AI Models' },
];

const systemNav = [
  { to: '/risk', icon: Shield, label: 'Risk Management' },
  { to: '/journal', icon: BookOpen, label: 'Journal' },
  { to: '/alerts', icon: Bell, label: 'Alerts' },
  { to: '/exchange', icon: Plug, label: 'Exchange' },
  { to: '/system', icon: Activity, label: 'System Health' },
  { to: '/users', icon: Users, label: 'Users' },
  { to: '/admin', icon: Shield, label: 'Admin' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

function NavSection({ title, items }: { title: string; items: Array<{ to: string; icon: React.ElementType; label: string }> }) {
  return (
    <div>
      <p className="px-4 py-2 text-[10px] font-semibold uppercase tracking-widest text-surface-500">
        {title}
      </p>
      <div className="space-y-0.5">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'text-primary-400 bg-primary-500/10 border border-primary-500/20'
                  : 'text-surface-400 hover:text-surface-100 hover:bg-surface-800/50'
              }`
            }
          >
            <item.icon className="w-4 h-4" />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </div>
    </div>
  );
}

export default function Sidebar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setMobileOpen(!mobileOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-surface-800 border border-surface-700"
        aria-label="Toggle navigation"
      >
        {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-black/60"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-full w-64 bg-surface-900/95 backdrop-blur-xl border-r border-surface-700/50 z-40 transform transition-transform duration-200 lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-6 py-6 border-b border-surface-700/50">
          <img src="/logo.svg" alt="BARAKA TRADING BOT" className="w-9 h-9" />
          <div>
            <h1 className="text-sm font-bold text-surface-100 tracking-tight">BARAKA TRADING BOT</h1>
            <p className="text-[10px] text-surface-500">Trading Platform</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          <NavSection title="Trading" items={tradingNav} />
          <NavSection title="Analysis" items={analysisNav} />
          <NavSection title="System" items={systemNav} />
        </nav>

        {/* Bottom section */}
        <div className="px-4 py-4 border-t border-surface-700/50">
          <div className="flex items-center gap-2 px-2">
            <div className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
            <span className="text-xs text-surface-500">Paper Trading Mode</span>
          </div>
        </div>
      </aside>
    </>
  );
}
