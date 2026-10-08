import { useState } from 'react'
import { motion } from 'framer-motion'
import { User, Bell, Shield, Palette, Key, Globe, Save } from 'lucide-react'

export default function Settings() {
  const [activeTab, setActiveTab] = useState('profile')

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'api', label: 'API Keys', icon: Key },
    { id: 'language', label: 'Language', icon: Globe },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Manage your account preferences</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Tabs */}
        <div className="glass-card p-4">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full nav-link ${activeTab === tab.id ? 'nav-link-active' : ''}`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="lg:col-span-3 glass-card">
          {activeTab === 'profile' && (
            <div className="card-body space-y-6">
              <h2 className="text-lg font-semibold text-surface-100">Profile Settings</h2>
              
              <div className="flex items-center gap-6">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                  <User className="w-10 h-10 text-white" />
                </div>
                <div>
                  <button className="btn-ghost text-sm">Change Avatar</button>
                  <p className="text-xs text-surface-500 mt-1">JPG, PNG or GIF. Max 2MB.</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm text-surface-400">Display Name</label>
                  <input type="text" defaultValue="Trader" className="input-field" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm text-surface-400">Email</label>
                  <input type="email" defaultValue="trader@baraka.ai" className="input-field" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm text-surface-400">Timezone</label>
                  <select className="input-field">
                    <option>UTC</option>
                    <option>EST (UTC-5)</option>
                    <option>PST (UTC-8)</option>
                    <option>CET (UTC+1)</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm text-surface-400">Currency</label>
                  <select className="input-field">
                    <option>USD</option>
                    <option>EUR</option>
                    <option>GBP</option>
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm text-surface-400">Bio</label>
                <textarea rows={3} className="input-field resize-none" placeholder="Tell us about yourself..." />
              </div>

              <div className="flex justify-end">
                <button className="btn-primary flex items-center gap-2">
                  <Save className="w-4 h-4" />
                  Save Changes
                </button>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="card-body space-y-6">
              <h2 className="text-lg font-semibold text-surface-100">Notification Preferences</h2>
              
              <div className="space-y-4">
                {[
                  { label: 'Trade Executions', desc: 'Get notified when your trades are executed' },
                  { label: 'AI Signals', desc: 'Receive AI-generated trading signals' },
                  { label: 'Price Alerts', desc: 'Alerts when prices hit your targets' },
                  { label: 'Portfolio Updates', desc: 'Daily portfolio performance summary' },
                  { label: 'Security Alerts', desc: 'Login and security notifications' },
                ].map((pref) => (
                  <div key={pref.label} className="flex items-center justify-between py-3 border-b border-surface-800/50 last:border-0">
                    <div>
                      <p className="font-medium text-surface-200">{pref.label}</p>
                      <p className="text-sm text-surface-500">{pref.desc}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked />
                      <div className="w-11 h-6 bg-surface-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-500"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="card-body space-y-6">
              <h2 className="text-lg font-semibold text-surface-100">Security Settings</h2>
              
              <div className="space-y-4">
                <div className="glass-card-sm p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-surface-200">Two-Factor Authentication</p>
                      <p className="text-sm text-surface-500">Add an extra layer of security</p>
                    </div>
                    <span className="badge-buy">Enabled</span>
                  </div>
                </div>
                <div className="glass-card-sm p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-surface-200">Login Notifications</p>
                      <p className="text-sm text-surface-500">Email on new device login</p>
                    </div>
                    <span className="badge-buy">Enabled</span>
                  </div>
                </div>
                <div className="glass-card-sm p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-surface-200">Withdrawal Whitelist</p>
                      <p className="text-sm text-surface-500">Only allow withdrawals to saved addresses</p>
                    </div>
                    <span className="badge-neutral">Disabled</span>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm text-surface-400">Change Password</label>
                <input type="password" placeholder="Current password" className="input-field" />
                <input type="password" placeholder="New password" className="input-field" />
                <input type="password" placeholder="Confirm new password" className="input-field" />
              </div>

              <div className="flex justify-end">
                <button className="btn-primary">Update Password</button>
              </div>
            </div>
          )}

          {activeTab === 'appearance' && (
            <div className="card-body space-y-6">
              <h2 className="text-lg font-semibold text-surface-100">Appearance</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-surface-400 mb-3 block">Theme</label>
                  <div className="grid grid-cols-3 gap-4">
                    {['Dark', 'Darker', 'Midnight'].map((theme) => (
                      <button
                        key={theme}
                        className={`glass-card-sm p-4 text-center transition-all ${theme === 'Dark' ? 'ring-2 ring-primary-500' : ''}`}
                      >
                        <div className="w-full h-16 rounded-lg bg-surface-800 mb-2" />
                        <span className="text-sm text-surface-300">{theme}</span>
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="text-sm text-surface-400 mb-3 block">Accent Color</label>
                  <div className="flex gap-3">
                    {['#10b981', '#22d3ee', '#8b5cf6', '#f59e0b', '#ef4444'].map((color) => (
                      <button
                        key={color}
                        className="w-10 h-10 rounded-full border-2 border-transparent hover:border-surface-400 transition-all"
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'api' && (
            <div className="card-body space-y-6">
              <h2 className="text-lg font-semibold text-surface-100">API Keys</h2>
              
              <div className="glass-card-sm p-4">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="font-medium text-surface-200">Trading Bot Key</p>
                    <p className="text-sm text-surface-500 font-mono">bk_live_****...****7f3a</p>
                  </div>
                  <div className="flex gap-2">
                    <button className="btn-ghost text-sm">Regenerate</button>
                    <button className="btn-danger text-sm">Revoke</button>
                  </div>
                </div>
                <p className="text-xs text-surface-500">Created: Jan 15, 2026 | Last used: 2 hours ago</p>
              </div>

              <button className="btn-primary">Create New API Key</button>
            </div>
          )}

          {activeTab === 'language' && (
            <div className="card-body space-y-6">
              <h2 className="text-lg font-semibold text-surface-100">Language & Region</h2>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm text-surface-400">Language</label>
                  <select className="input-field">
                    <option>English</option>
                    <option>العربية</option>
                    <option>中文</option>
                    <option>Español</option>
                    <option>Français</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm text-surface-400">Date Format</label>
                  <select className="input-field">
                    <option>MM/DD/YYYY</option>
                    <option>DD/MM/YYYY</option>
                    <option>YYYY-MM-DD</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
