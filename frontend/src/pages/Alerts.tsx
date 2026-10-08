import { useState } from 'react';
import { motion } from 'framer-motion';
import { Bell, CheckCircle, AlertTriangle, XCircle, Info, Filter } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import EmptyState from '../components/EmptyState';
import type { Alert } from '../types';

const demoAlerts: Alert[] = [
  { id: 'alert-001', type: 'signal', title: 'High-Confidence BUY Signal', message: 'BTC/USDT: BUY signal generated with 78% confidence. Trend Following strategy, R:R 1:2.4.', severity: 'info', read: false, created_at: new Date(Date.now() - 1800000).toISOString() },
  { id: 'alert-002', type: 'trade_opened', title: 'Trade Opened', message: 'BTC/USDT long position opened at ,432. Quantity: 0.029 BTC. Stop loss: ,200.', severity: 'info', read: false, created_at: new Date(Date.now() - 3600000).toISOString() },
  { id: 'alert-003', type: 'trade_closed', title: 'Trade Closed', message: 'ETH/USDT long position closed at ,542. P&L: +.36 (+0.91%). Exit reason: Signal.', severity: 'info', read: true, created_at: new Date(Date.now() - 7200000).toISOString() },
  { id: 'alert-004', type: 'drawdown', title: 'Drawdown Warning', message: 'Portfolio drawdown reached 4.5%. Approaching 10% maximum drawdown limit.', severity: 'warning', read: false, created_at: new Date(Date.now() - 10800000).toISOString() },
  { id: 'alert-005', type: 'stop_loss', title: 'Stop Loss Triggered', message: 'SOL/USDT long position stopped out at . Loss: -.80 (-1.71%).', severity: 'critical', read: true, created_at: new Date(Date.now() - 14400000).toISOString() },
  { id: 'alert-006', type: 'exchange', title: 'Exchange Connected', message: 'Binance testnet connection established. WebSocket feed active.', severity: 'info', read: true, created_at: new Date(Date.now() - 18000000).toISOString() },
  { id: 'alert-007', type: 'model', title: 'Model Drift Detected', message: 'BARAKA Range Detector v1.2.0 showing medium feature drift. Monitoring closely.', severity: 'warning', read: true, created_at: new Date(Date.now() - 21600000).toISOString() },
  { id: 'alert-008', type: 'kill_switch', title: 'Kill Switch Ready', message: 'Kill switch is armed and functioning. All systems nominal.', severity: 'info', read: true, created_at: new Date(Date.now() - 25200000).toISOString() },
];

const severityConfig = {
  info: { icon: Info, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/20' },
  warning: { icon: AlertTriangle, color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20' },
  critical: { icon: XCircle, color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/20' },
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
          description="Alerts will appear here when events occur."
        />
      ) : (
        <div className="space-y-2">
          {filteredAlerts.map((alert, i) => {
            const config = severityConfig[alert.severity];
            const Icon = config.icon;
            return (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                <GlassCard className={p-4 }>
                  <div className="flex items-start gap-3">
                    <div className={lex h-8 w-8 items-center justify-center rounded-lg   flex-shrink-0}>
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
