import { motion } from 'framer-motion';
import { ArrowLeftRight, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import EmptyState from '../components/EmptyState';
import type { Position } from '../types';

const demoPositions: Position[] = [
  { position_id: 'pos-001', symbol: 'BTC/USDT', side: 'long', quantity: 0.029, entry_price: 66800, current_price: 67432, stop_loss: 66200, take_profit: 70500, unrealized_pnl: 18.33, unrealized_pnl_percent: 0.95, leverage: 1, opened_at: new Date(Date.now() - 7200000).toISOString(), strategy: 'Trend Following' },
  { position_id: 'pos-002', symbol: 'ETH/USDT', side: 'long', quantity: 0.23, entry_price: 3510, current_price: 3542, stop_loss: 3480, take_profit: 3680, unrealized_pnl: 7.36, unrealized_pnl_percent: 0.91, leverage: 1, opened_at: new Date(Date.now() - 14400000).toISOString(), strategy: 'Pullback' },
  { position_id: 'pos-003', symbol: 'SOL/USDT', side: 'short', quantity: 5.6, entry_price: 182, current_price: 178.45, stop_loss: 185, take_profit: 170, unrealized_pnl: 19.88, unrealized_pnl_percent: 1.98, leverage: 1, opened_at: new Date(Date.now() - 28800000).toISOString(), strategy: 'Breakout' },
];

export default function Positions() {
  const totalUnrealized = demoPositions.reduce((sum, p) => sum + p.unrealized_pnl, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Open Positions</h1>
          <p className="text-sm text-slate-400">{demoPositions.length} open positions</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-slate-500">Total Unrealized P&L</p>
          <p className={`text-lg font-bold ${totalUnrealized >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {totalUnrealized >= 0 ? '+' : ''}${totalUnrealized.toFixed(2)}
          </p>
        </div>
      </div>

      {demoPositions.length === 0 ? (
        <EmptyState
          icon={<ArrowLeftRight className="h-8 w-8" />}
          title="No open positions"
          description="Open a position from the Trading page or wait for AI signals to generate trades."
        />
      ) : (
        <div className="space-y-3">
          {demoPositions.map((pos, i) => (
            <motion.div
              key={pos.position_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <GlassCard className="p-4" hover>
                <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                  <div className="flex items-center gap-3 flex-1">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${
                      pos.side === 'long' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                    }`}>
                      {pos.side === 'long' ? <ArrowUpRight className="h-5 w-5" /> : <ArrowDownRight className="h-5 w-5" />}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-bold text-white">{pos.symbol}</h3>
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                          pos.side === 'long' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                        }`}>
                          {pos.side.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500">{pos.strategy} • Opened {new Date(pos.opened_at).toLocaleString()}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-6 text-sm">
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Quantity</p>
                      <p className="font-semibold text-white">{pos.quantity}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Entry</p>
                      <p className="font-semibold text-white">${pos.entry_price.toLocaleString()}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Current</p>
                      <p className="font-semibold text-white">${pos.current_price.toLocaleString()}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Stop Loss</p>
                      <p className="font-semibold text-red-400">${pos.stop_loss.toLocaleString()}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Take Profit</p>
                      <p className="font-semibold text-emerald-400">${pos.take_profit.toLocaleString()}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">P&L</p>
                      <p className={`font-bold ${pos.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {pos.unrealized_pnl >= 0 ? '+' : ''}${pos.unrealized_pnl.toFixed(2)}
                      </p>
                      <p className={`text-xs ${pos.unrealized_pnl_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {pos.unrealized_pnl_percent >= 0 ? '+' : ''}{pos.unrealized_pnl_percent.toFixed(2)}%
                      </p>
                    </div>
                  </div>

                  <button className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs text-slate-400 hover:text-red-400 hover:border-red-500/50 transition-colors">
                    Close
                  </button>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
