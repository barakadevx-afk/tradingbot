import { useState } from 'react';
import { motion } from 'framer-motion';
import { Plug, Shield, Plus } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';

const exchanges = [
  { id: '1', name: 'Binance', status: 'connected' as const, testnet: true, latency: 45 },
  { id: '2', name: 'Bybit', status: 'disconnected' as const, testnet: true, latency: 0 },
];

export default function Exchange() {
  const [showAddModal, setShowAddModal] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Exchange Connections</h1>
          <p className="text-sm text-slate-400">Manage your exchange API connections</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-400 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Add Exchange
        </button>
      </div>

      <GlassCard className="p-4">
        <div className="flex items-start gap-3">
          <Shield className="h-5 w-5 text-emerald-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-white">Security Notice</h3>
            <p className="text-xs text-slate-400 mt-1">
              API keys are encrypted and stored securely. They are never exposed to the frontend.
            </p>
          </div>
        </div>
      </GlassCard>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {exchanges.map((exchange) => (
          <motion.div
            key={exchange.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            <GlassCard className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-800">
                    <Plug className="h-6 w-6 text-slate-400" />
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
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Latency</span>
                  <span className="font-semibold text-white">{exchange.latency}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Status</span>
                  <span className={exchange.status === 'connected' ? 'text-emerald-400' : 'text-slate-500'}>
                    {exchange.status === 'connected' ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-bold text-white mb-4">Add Exchange</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Exchange</label>
                <select className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white">
                  <option>Binance</option>
                  <option>Bybit</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">API Key</label>
                <input type="text" placeholder="Enter API key" className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">API Secret</label>
                <input type="password" placeholder="Enter API secret" className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white" />
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3">
              <button onClick={() => setShowAddModal(false)} className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300">
                Cancel
              </button>
              <button onClick={() => setShowAddModal(false)} className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white">
                Connect
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
