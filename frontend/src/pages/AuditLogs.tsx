import { useState } from 'react';
import { motion } from 'framer-motion';
import { ScrollText, Search, Download, Filter } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import type { AuditLog } from '../types';

const demoAuditLogs: AuditLog[] = [
  { id: 'log-001', user_id: 'user-001', action: 'LOGIN', resource: 'auth', details: 'Successful login from 192.168.1.100', ip_address: '192.168.1.100', created_at: new Date(Date.now() - 1800000).toISOString() },
  { id: 'log-002', user_id: 'user-001', action: 'RISK_CONFIG_CHANGED', resource: 'risk', details: 'Updated max_daily_loss from 5% to 3%', ip_address: '192.168.1.100', created_at: new Date(Date.now() - 3600000).toISOString() },
  { id: 'log-003', user_id: 'user-002', action: 'TRADE_OPENED', resource: 'trading', details: 'Paper trade opened: BTC/USDT long 0.029 BTC at ,432', ip_address: '192.168.1.101', created_at: new Date(Date.now() - 7200000).toISOString() },
  { id: 'log-004', user_id: 'user-001', action: 'STRATEGY_ENABLED', resource: 'strategies', details: 'Enabled strategy: Breakout v2', ip_address: '192.168.1.100', created_at: new Date(Date.now() - 10800000).toISOString() },
  { id: 'log-005', user_id: 'user-001', action: 'MODEL_APPROVED', resource: 'models', details: 'Approved model: BARAKA Trend Predictor v2.1.0', ip_address: '192.168.1.100', created_at: new Date(Date.now() - 14400000).toISOString() },
  { id: 'log-006', user_id: 'user-002', action: 'TRADE_CLOSED', resource: 'trading', details: 'Paper trade closed: ETH/USDT long, P&L: +.36', ip_address: '192.168.1.101', created_at: new Date(Date.now() - 18000000).toISOString() },
  { id: 'log-007', user_id: 'user-001', action: 'API_KEY_ADDED', resource: 'exchange', details: 'Binance testnet API key added (READ, TRADE permissions)', ip_address: '192.168.1.100', created_at: new Date(Date.now() - 21600000).toISOString() },
  { id: 'log-008', user_id: 'user-001', action: 'KILL_SWITCH_ACTIVATED', resource: 'system', details: 'Kill switch activated due to drawdown warning', ip_address: '192.168.1.100', created_at: new Date(Date.now() - 25200000).toISOString() },
  { id: 'log-009', user_id: 'user-001', action: 'KILL_SWITCH_DEACTIVATED', resource: 'system', details: 'Kill switch deactivated after system review', ip_address: '192.168.1.100', created_at: new Date(Date.now() - 25200000).toISOString() },
  { id: 'log-010', user_id: 'user-003', action: 'FAILED_LOGIN', resource: 'auth', details: 'Failed login attempt for analyst@baraka.ai', ip_address: '10.0.0.50', created_at: new Date(Date.now() - 28800000).toISOString() },
  { id: 'log-011', user_id: 'user-001', action: 'USER_CREATED', resource: 'users', details: 'Created new user: viewer@baraka.ai (VIEWER role)', ip_address: '192.168.1.100', created_at: new Date(Date.now() - 32400000).toISOString() },
  { id: 'log-012', user_id: 'user-001', action: 'LIVE_MODE_DISABLED', resource: 'trading', details: 'Live trading mode disabled', ip_address: '192.168.1.100', created_at: new Date(Date.now() - 36000000).toISOString() },
];

const actionColors: Record<string, string> = {
  LOGIN: 'text-emerald-400 bg-emerald-500/10',
  FAILED_LOGIN: 'text-red-400 bg-red-500/10',
  TRADE_OPENED: 'text-emerald-400 bg-emerald-500/10',
  TRADE_CLOSED: 'text-blue-400 bg-blue-500/10',
  RISK_CONFIG_CHANGED: 'text-amber-400 bg-amber-500/10',
  STRATEGY_ENABLED: 'text-emerald-400 bg-emerald-500/10',
  STRATEGY_DISABLED: 'text-red-400 bg-red-500/10',
  MODEL_APPROVED: 'text-emerald-400 bg-emerald-500/10',
  MODEL_RETIRED: 'text-red-400 bg-red-500/10',
  API_KEY_ADDED: 'text-cyan-400 bg-cyan-500/10',
  API_KEY_REMOVED: 'text-red-400 bg-red-500/10',
  KILL_SWITCH_ACTIVATED: 'text-red-400 bg-red-500/10',
  KILL_SWITCH_DEACTIVATED: 'text-emerald-400 bg-emerald-500/10',
  USER_CREATED: 'text-cyan-400 bg-cyan-500/10',
  ROLE_CHANGED: 'text-amber-400 bg-amber-500/10',
  LIVE_MODE_ENABLED: 'text-red-400 bg-red-500/10',
  LIVE_MODE_DISABLED: 'text-emerald-400 bg-emerald-500/10',
};

export default function AuditLogs() {
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState('all');

  const actions = [...new Set(demoAuditLogs.map((l) => l.action))];

  const filtered = demoAuditLogs.filter((log) => {
    if (search && !log.details.toLowerCase().includes(search.toLowerCase()) && !log.action.toLowerCase().includes(search.toLowerCase())) return false;
    if (actionFilter !== 'all' && log.action !== actionFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Audit Logs</h1>
          <p className="text-sm text-slate-400">Immutable record of all important system actions</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors">
          <Download className="h-4 w-4" />
          Export Logs
        </button>
      </div>

      {/* Filters */}
      <GlassCard className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search audit logs..."
              className="w-full rounded-lg border border-slate-700 bg-slate-900/50 pl-10 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
            />
          </div>
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
          >
            <option value="all">All Actions</option>
            {actions.map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
        </div>
      </GlassCard>

      {/* Logs Table */}
      <GlassCard className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/50">
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Timestamp</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Action</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Resource</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Details</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filtered.map((log, i) => (
                <motion.tr
                  key={log.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: i * 0.02 }}
                  className="hover:bg-slate-800/30 transition-colors"
                >
                  <td className="px-4 py-3 text-xs text-slate-500 whitespace-nowrap">
                    {new Date(log.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <span className={inline-flex items-center rounded px-2 py-0.5 text-[10px] font-bold }>
                      {log.action}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">
                    {log.resource}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-300 max-w-md">
                    {log.details}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500 font-mono">
                    {log.ip_address}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
