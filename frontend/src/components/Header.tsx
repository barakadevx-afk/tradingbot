import { Bell, Search, User, ChevronDown } from 'lucide-react'

export default function Header() {
  return (
    <header className="sticky top-0 z-30 bg-surface-950/80 backdrop-blur-xl border-b border-surface-700/50">
      <div className="flex items-center justify-between px-8 py-4">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-500" />
            <input
              type="text"
              placeholder="Search markets, assets..."
              className="input-field pl-10"
            />
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-surface-800/50 transition-colors">
            <Bell className="w-5 h-5 text-surface-400" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary-500 rounded-full" />
          </button>

          {/* User menu */}
          <button className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-surface-800/50 transition-colors">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
              <User className="w-4 h-4 text-white" />
            </div>
            <div className="text-left hidden sm:block">
              <p className="text-sm font-medium text-surface-200">Trader</p>
              <p className="text-xs text-surface-500">Pro Plan</p>
            </div>
            <ChevronDown className="w-4 h-4 text-surface-500" />
          </button>
        </div>
      </div>
    </header>
  )
}
