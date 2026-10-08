import { useState } from 'react';
import { motion } from 'framer-motion';
import { ScrollText, ArrowUpRight, ArrowDownRight, Filter } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import EmptyState from '../components/EmptyState';
import type { Trade } from '../types';

const demoTrades: Trade[] = [
  { trade_id: 'trade-001', symbol: 'BTC/USDT', direction: 'long', entry_price: 66800, exit_price: 67432, quantity: 0.029, stop_loss: 66200, take_profit: 70500, strategy: 'Trend Following', ai_model: 'v2.1.0', signal_confidence: 78, market_regime: 'TREND_UP', fees: 0.68, slippage: 3, profit_loss: 18.33, return_percent: 0.95, risk_percent: 0.5, duration: '2h 15m', exit_reason: 'Signal', opened_at: new Date(Date.now() - 7200000).toISOString(), closed_at: new Date(Date.now() - 3600000).toISOString() },
  { trade_id: 'trade-002', symbol: 'ETH/USDT', direction: 'long', entry_price: 3510, exit_price: 3542, quantity: 0.23, stop_loss: 3480, take_profit: 3680, strategy: 'Pullback', ai_model: 'v2.1.0', signal_confidence: 72, market_regime: 'TREND_UP', fees: 0.40, slippage: 2, profit_loss: 7.36, return_percent: 0.91, risk_percent: 0.5, duration: '4h 30m', exit_reason: 'Signal', opened_at: new Date(Date.now() - 14400000).toISOString(), closed_at: new Date(Date.now() - 7200000).toISOString() },
  { trade_id: 'trade-003', symbol: 'BTC/USDT', direction: 'short', entry_price: 68100, exit_price: 67500, quantity: 0.015, stop_loss: 69500, take_profit: 65000, strategy: 'Trend Following', ai_model: 'v2.1.0', signal_confidence: 81, market_regime: 'TREND_DOWN', fees: 0.51, slippage: 5, profit_loss: 9.00, return_percent: 1.0, risk_percent: 0.5, duration: '6h 45m', exit_reason: 'Take Profit', opened_at: new Date(Date.now() - 21600000).toISOString(), closed_at: new Date(Date.now() - 14400000).toISOString() },
  { trade_id: 'trade-004', symbol: 'SOL/USDT', direction: 'long', entry_price: 175, exit_price: 172, quantity: 5.6, stop_loss: 170, take_profit: 190, strategy: 'Breakout', ai_model: 'v2.1.0', signal_confidence: 65, market_regime: 'BREAKOUT', fees: 0.35, slippage: 1.5, profit_loss: -16.80, return_percent: -1.71, risk_percent: 0.5, duration: '3h 20m', exit_reason: 'Stop Loss', opened_at: new Date(Date.now() - 28800000).toISOString(), closed_at: new Date(Date.now() - 25200000).toISOString() },
  { trade_id: 'trade-005', symbol: 'BNB/USDT', direction: 'long', entry_price: 605, exit_price: 612, quantity: 1.2, stop_loss: 600, take_profit: 625, strategy: 'Pullback', ai_model: 'v2.1.0', signal_confidence: 68, market_regime: 'RANGE', fees: 0.22, slippage: 0.8, profit_loss: 8.40, return_percent: 1.16, risk_percent: 0.5, duration: '5h 10m', exit_reason: 'Signal', opened_at: new Date(Date.now() - 36000000).toISOString(), closed_at: new Date(Date.now() - 32400000).toISOString() },
];

export default function Trades() {
  const [filter, setFilter] = useState('all');

  const filteredTrades = demoTrades.filter((t) => {
    if (filter === 'all') return true;
    if (filter === 'profit') return t.profit_loss > 0;
    if (filter === 'loss') return t.profit_loss < 0;
    return true;
  });

  const totalPnl = demoTrades.reduce((sum, t) => sum + t.profit_loss, 0);
  const winRate = (demoTrades.filter((t) => t.profit_loss > 0).length / demoTrades.length) * 100;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Trade History</h1>
          <p className="text-sm text-slate-400">{demoTrades.length} trades • Win rate: {winRate.toFixed(1)}%</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
          >
            <option value="all">All Trades</option>
            <option value="profit">Profitable</option>
            <option value="loss">Losses</option>
          </select>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <GlassCard className="p-4">
          <p className="text-xs text-slate-500">Total P&L</p>
          <p className={`text-xl font-bold ${totalPnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(2)}
          </p>
        </GlassCard>
        <GlassCard className="p-4">
          <p className="text-xs text-slate-500">Win Rate</p>
          <p className="text-xl font-bold text-white">{winRate.toFixed(1)}%</p>
        </GlassCard>
        <GlassCard className="p-4">
          <p className="text-xs text-slate-500">Total Trades</p>
          <p className="text-xl font-bold text-white">{demoTrades.length}</p>
        </GlassCard>
      </div>

      {filteredTrades.length === 0 ? (
        <EmptyState
          icon={<ScrollText className="h-8 w-8" />}
          title="No trades found"
          description="Trades will appear here after execution."
        />
      ) : (
        <div className="space-y-3">
          {filteredTrades.map((trade, i) => (
            <motion.div
              key={trade.trade_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <GlassCard className="p-4" hover>
                <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                  <div className="flex items-center gap-3 flex-1">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${
                      trade.direction === 'long' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                    }`}>
                      {trade.direction === 'long' ? <ArrowUpRight className="h-5 w-5" /> : <ArrowDownRight className="h-5 w-5" />}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-bold text-white">{trade.symbol}</h3>
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                          trade.direction === 'long' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                        }`}>
                          {trade.direction.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500">
                        {trade.strategy} • {trade.market_regime} • Confidence: {trade.signal_confidence}%
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-6 text-sm">
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Entry</p>
                      <p className="font-semibold text-white">${trade.entry_price.toLocaleString()}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Exit</p>
                      <p className="font-semibold text-white">${trade.exit_price.toLocaleString()}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Qty</p>
                      <p className="font-semibold text-white">{trade.quantity}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Fees</p>
                      <p className="font-semibold text-white">${trade.fees.toFixed(2)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Duration</p>
                      <p className="font-semibold text-white">{trade.duration}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">P&L</p>
                      <p className={`font-bold ${trade.profit_loss >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {trade.profit_loss >= 0 ? '+' : ''}${trade.profit_loss.toFixed(2)}
                      </p>
                      <p className={`text-xs ${trade.return_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {trade.return_percent >= 0 ? '+' : ''}{trade.return_percent.toFixed(2)}%
                      </p>
                    </div>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-slate-800/50 flex items-center justify-between text-xs text-slate-500">
                  <span>Exit: {trade.exit_reason}</span>
                  <span>Opened: {new Date(trade.opened_at).toLocaleString()}</span>
                  <span>Closed: {new Date(trade.closed_at).toLocaleString()}</span>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
