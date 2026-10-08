import { useState } from 'react';
import { motion } from 'framer-motion';
import { Plug, Shield, Key, Trash2, Plus, CheckCircle, XCircle, AlertTriangle, ExternalLink } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import EmptyState from '../components/EmptyState';

const exchanges = [
  {
    id: 'binance',
    name: 'Binance',
    status: 'connected',
    testnet: true,
    permissions: ['read', 'trade'],
    connectedAt: new Date(Date.now() - 86400000).toISOString(),
    lastPing: new Date(Date.now() - 5000).toISOString(),
    latency: 45,
  },
  {
    id: 'bybit',
    name: 'Bybit',
    status: 'disconnected',
    testnet: true,
    permissions: ['read'],
    connectedAt: null,
    lastPing: null,
    latency: 0,
  },
];

export default function Exchange() {
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedExchange, setSelectedExchange] = useState<string | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Exchange Connections</h1>
          <p className="text-sm text-slate-400">Manage exchange API connections and permissions</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-400 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Exchange
        </button>
      </div>

      {/* Security Notice */}
      <GlassCard className="p-4">
        <div className="flex items-start gap-3">
          <Shield className="h-5 w-5 text-emerald-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-white">Security Notice</h3>
            <p className="text-xs text-slate-400 mt-1">
              API keys are encrypted before storage and never exposed to the frontend. Withdrawals are never required for BARAKA AI trading.
              Only READ and TRADING permissions are needed.
            </p>
          </div>
        </div>
      </GlassCard>

      {/* Exchange Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {exchanges.map((exchange, i) => (
          <motion.div
            key={exchange.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <GlassCard className="p-6" hover>
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={lex h-12 w-12 items-center justify-center rounded-xl }>
                    <Plug className={h-6 w-6 } />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">{exchange.name}</h3>
                    <div className="flex items-center gap-2">
                      <StatusBadge status={exchange.status === 'connected' ? 'HEALTHY' : 'OFFLINE'} size="sm" />
                      {exchange.testnet && (
                        <span className="text-[10px] font-semibold text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded">TESTNET</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Permissions</span>
                  <div className="flex gap-1">
                    {exchange.permissions.map((p) => (
                      <span key={p} className="text-xs font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                        {p.toUpperCase()}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Latency</span>
                  <span className="font-semibold text-white">{exchange.latency}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Connected</span>
                  <span className="font-semibold text-white">
                    {exchange.connectedAt ? new Date(exchange.connectedAt).toLocaleDateString() : 'Never'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Last Ping</span>
                  <span className="font-semibold text-white">
                    {exchange.lastPing ? new Date(exchange.lastPing).toLocaleTimeString() : '—'}
                  </span>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-slate-800 flex items-center gap-2">
                {exchange.status === 'connected' ? (
                  <>
                    <button className="flex-1 rounded-lg border border-slate-700 px-3 py-2 text-xs text-slate-300 hover:bg-slate-800 transition-colors">
                      Test Connection
                    </button>
                    <button className="flex-1 rounded-lg border border-red-500/30 px-3 py-2 text-xs text-red-400 hover:bg-red-500/10 transition-colors">
                      Disconnect
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setSelectedExchange(exchange.id)}
                    className="flex-1 rounded-lg bg-emerald-500 px-3 py-2 text-xs font-semibold text-white hover:bg-emerald-400 transition-colors"
                  >
                    Connect
                  </button>
                )}
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* API Key Management */}
      <GlassCard className="p-6">
        <h2 className="text-lg font-semibold text-white mb-4">API Key Management</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-lg bg-slate-800/30 p-3">
            <div className="flex items-center gap-3">
              <Key className="h-4 w-4 text-slate-500" />
              <div>
                <p className="text-sm text-white">Binance API Key</p>
                <p className="text-xs text-slate-500">•••••••••••••••••••••••• • Added {new Date(Date.now() - 86400000).toLocaleDateString()}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-emerald-400" />
              <button className="text-xs text-red-400 hover:text-red-300 transition-colors">Remove</button>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Add Exchange Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl"
          >
            <h2 className="text-xl font-bold text-white mb-4">Add Exchange Connection</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Exchange</label>
                <select className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none">
                  <option value="binance">Binance</option>
                  <option value="bybit">Bybit</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">API Key</label>
                <input
                  type="text"
                  placeholder="Enter API key"
                  className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">API Secret</label>
                <input
                  type="password"
                  placeholder="Enter API secret"
                  className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="testnet" defaultChecked className="rounded border-slate-700 bg-slate-900" />
                <label htmlFor="testnet" className="text-sm text-slate-300">Use Testnet</label>
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowAddModal(false)}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowAddModal(false)}
                className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-400 transition-colors"
              >
                Connect
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
