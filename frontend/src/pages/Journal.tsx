import { Download } from 'lucide-react';
import GlassCard from '../components/GlassCard';

const journalEntries = [
  { id: '1', date: '2024-01-15', symbol: 'BTC/USDT', side: 'Long' as const, entry: 67432, exit: null, pnl: null, status: 'open' as const, strategy: 'Trend Following', confidence: 78 },
  { id: '2', date: '2024-01-14', symbol: 'ETH/USDT', side: 'Long' as const, entry: 3510, exit: 3542, pnl: 7.36, status: 'closed' as const, strategy: 'Pullback', confidence: 72 },
  { id: '3', date: '2024-01-14', symbol: 'SOL/USDT', side: 'Short' as const, entry: 182, exit: 178.45, pnl: 19.88, status: 'closed' as const, strategy: 'Breakout', confidence: 65 },
  { id: '4', date: '2024-01-13', symbol: 'BTC/USDT', side: 'Long' as const, entry: 65200, exit: 64800, pnl: -10.0, status: 'closed' as const, strategy: 'Trend Following', confidence: 74 },
  { id: '5', date: '2024-01-12', symbol: 'BNB/USDT', side: 'Long' as const, entry: 605, exit: 612, pnl: 8.4, status: 'closed' as const, strategy: 'Pullback', confidence: 68 },
];

export default function Journal() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Trading Journal</h1>
          <p className="text-sm text-slate-400">Review your past trades and decisions</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors">
          <Download className="h-4 w-4" />
          Export
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <GlassCard className="p-4">
          <p className="text-xs text-slate-500">Total Trades</p>
          <p className="text-xl font-bold text-white mt-1">{journalEntries.length}</p>
        </GlassCard>
        <GlassCard className="p-4">
          <p className="text-xs text-slate-500">Win Rate</p>
          <p className="text-xl font-bold text-emerald-400 mt-1">60%</p>
        </GlassCard>
        <GlassCard className="p-4">
          <p className="text-xs text-slate-500">Net P&L</p>
          <p className="text-xl font-bold text-emerald-400 mt-1">+$25.64</p>
        </GlassCard>
        <GlassCard className="p-4">
          <p className="text-xs text-slate-500">Avg Confidence</p>
          <p className="text-xl font-bold text-white mt-1">71%</p>
        </GlassCard>
      </div>

      <GlassCard className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/50">
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Date</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Symbol</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Side</th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Entry</th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Exit</th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">P&L</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Strategy</th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-slate-500">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {journalEntries.map((entry) => (
                <tr key={entry.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3 text-xs text-slate-500">{entry.date}</td>
                  <td className="px-4 py-3 text-sm font-medium text-white">{entry.symbol}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-semibold ${entry.side === 'Long' ? 'text-emerald-400' : 'text-red-400'}`}>
                      {entry.side}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-300 text-right">${entry.entry.toLocaleString()}</td>
                  <td className="px-4 py-3 text-sm text-slate-300 text-right">
                    {entry.exit ? `$${entry.exit.toLocaleString()}` : '—'}
                  </td>
                  <td className="px-4 py-3 text-sm text-right">
                    {entry.pnl !== null ? (
                      <span className={entry.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}>
                        {entry.pnl >= 0 ? '+' : ''}${entry.pnl.toFixed(2)}
                      </span>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">{entry.strategy}</td>
                  <td className="px-4 py-3 text-center">
                    <span className={`text-xs font-semibold px-2 py-1 rounded ${entry.status === 'open' ? 'bg-amber-500/10 text-amber-400' : 'bg-slate-800 text-slate-400'}`}>
                      {entry.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
