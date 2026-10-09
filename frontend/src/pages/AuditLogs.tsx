import { useState } from 'react';
import { Search, Download } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import type { AuditLog } from '../types';

const demoAuditLogs: AuditLog[] = [
  { id: '1', user_id: '1', action: 'LOGIN', resource: 'auth', details: 'User logged in successfully', ip_address: '192.168.1.1', created_at: '2024-01-15T10:30:00Z' },
  { id: '2', user_id: '2', action: 'TRADE_OPENED', resource: 'trading', details: 'Opened BTC/USDT position', ip_address: '192.168.1.2', created_at: '2024-01-15T09:15:00Z' },
  { id: '3', user_id: '1', action: 'RISK_UPDATED', resource: 'risk', details: 'Updated max drawdown to 10%', ip_address: '192.168.1.1', created_at: '2024-01-14T16:45:00Z' },
  { id: '4', user_id: '3', action: 'BACKTEST_RUN', resource: 'backtesting', details: 'Ran backtest for Trend Following strategy', ip_address: '192.168.1.3', created_at: '2024-01-14T14:20:00Z' },
  { id: '5', user_id: '1', action: 'USER_CREATED', resource: 'users', details: 'Created new user: trader2@baraka.ai', ip_address: '192.168.1.1', created_at: '2024-01-13T08:00:00Z' },
];

export default function AuditLogs() {
  const [search, setSearch] = useState('');

  const filtered = demoAuditLogs.filter((log) =>
    log.action.toLowerCase().includes(search.toLowerCase()) ||
    log.details.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Audit Logs</h1>
          <p className="text-sm text-slate-400">Track all system activities and user actions</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors">
          <Download className="h-4 w-4" />
          Export
        </button>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search logs..."
          className="w-full rounded-lg border border-slate-700 bg-slate-900/50 pl-10 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
        />
      </div>

      <GlassCard className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/50">
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">User</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Action</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Details</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filtered.map((log) => (
                <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3 text-sm text-white">{log.user_id}</td>
                  <td className="px-4 py-3">
                    <span className="text-xs font-semibold px-2 py-1 rounded bg-slate-800 text-slate-300">
                      {log.action}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-400">{log.details}</td>
                  <td className="px-4 py-3 text-xs text-slate-500">{new Date(log.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
