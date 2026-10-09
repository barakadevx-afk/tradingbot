import { useState } from 'react';
import { motion } from 'framer-motion';
import { Bell, CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import EmptyState from '../components/EmptyState';
import type { Alert } from '../types';

const demoAlerts: Alert[] = [
  { id: 'alert-001', type: 'signal', title: 'New signal generated', message: 'A new trading signal has been generated for BTC/USDT.', severity: 'info', read: false, created_at: '2024-01-15T10:30:00Z' },
  { id: 'alert-002', type: 'trade_opened', title: 'Trade opened', message: 'Your paper trade for ETH/USDT has been opened.', severity: 'info', read: false, created_at: '2024-01-15T09:15:00Z' },
  { id: 'alert-003', type: 'stop_loss', title: 'Stop loss triggered', message: 'Stop loss was triggered on SOL/USDT position.', severity: 'critical', read: true, created_at: '2024-01-14T16:45:00Z' },
  { id: 'alert-004', type: 'drawdown', title: 'Drawdown warning', message: 'Portfolio drawdown has reached 5%.', severity: 'warning', read: true, created_at: '2024-01-14T14:20:00Z' },
  { id: 'alert-005', type: 'system', title: 'System update', message: 'The trading engine has been updated to v2.1.', severity: 'info', read: true, created_at: '2024-01-13T08:00:00Z' },
];

const severityConfig = {
  info: { icon: Info, color: 'text-blue-400', bg: 'bg-blue-500/10' },
  warning: { icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-500/10' },
  critical: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10' },
};

export default function Alerts() {
  const [filter, setFilter] = useState('all');
  const [alerts, setAlerts] = useState(demoAlerts);

  const filteredAlerts = alerts.filter((a) => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !a.read;
    return a.severity === filter;
  });

  const markRead = (id: string) => {
    setAlerts((prev) => prev.map((a) => a.id === id ? { ...a, read: true } : a));
  };

  const markAllRead = () => {
    setAlerts((prev) => prev.map((a) => ({ ...a, read: true })));
  };

  const unreadCount = alerts.filter((a) => !a.read).length;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Alerts</h1>
          <p className="text-sm text-slate-400">{unreadCount} unread alerts</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
          >
            <option value="all">All Alerts</option>
            <option value="unread">Unread</option>
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="critical">Critical</option>
          </select>
          <button
            onClick={markAllRead}
            className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
          >
            <CheckCircle className="h-4 w-4" />
            Mark All Read
          </button>
        </div>
      </div>

      {filteredAlerts.length === 0 ? (
        <EmptyState
          icon={<Bell className="h-8 w-8" />}
          title="No alerts"
          description="You're all caught up. New alerts will appear here."
        />
      ) : (
        <div className="space-y-2">
          {filteredAlerts.map((alert) => {
            const config = severityConfig[alert.severity];
            const Icon = config.icon;
            return (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
              >
                <GlassCard className="p-4">
                  <div className="flex items-start gap-3">
                    <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${config.bg} ${config.color}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="text-sm font-semibold text-white">{alert.title}</h3>
                        {!alert.read && <span className="h-2 w-2 rounded-full bg-emerald-400" />}
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">{alert.message}</p>
                      <p className="text-[10px] text-slate-600 mt-1">
                        {new Date(alert.created_at).toLocaleString()}
                      </p>
                    </div>
                    {!alert.read && (
                      <button
                        onClick={() => markRead(alert.id)}
                        className="text-xs text-slate-500 hover:text-white transition-colors"
                      >
                        Mark read
                      </button>
                    )}
                  </div>
                </GlassCard>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
