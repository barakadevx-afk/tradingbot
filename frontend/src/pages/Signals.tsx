import { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Search } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import ConfidenceMeter from '../components/ConfidenceMeter';
import EmptyState from '../components/EmptyState';
import type { Signal } from '../types';

const demoSigs: Signal[] = [
  { signal_id: 'sig-001', symbol: 'BTC/USDT', timestamp: new Date(Date.now() - 3600000).toISOString(), timeframe: '4H', signal: 'BUY', entry_price: 67432, stop_loss: 66200, take_profit: 70500, risk_reward: 2.4, confidence: 78, market_regime: 'TREND_UP', strategy: 'Trend Following', model_version: 'v2.1.0', reasoning_summary: 'Bullish 4H trend, EMA20 above EMA50, RSI 61, rising volume, ATR within acceptable range, BUY probability 76%, risk/reward 1:2.4.', status: 'active', buy_probability: 76, sell_probability: 12, hold_probability: 12 },
  { signal_id: 'sig-002', symbol: 'ETH/USDT', timestamp: new Date(Date.now() - 7200000).toISOString(), timeframe: '1H', signal: 'BUY', entry_price: 3542, stop_loss: 3480, take_profit: 3680, risk_reward: 2.1, confidence: 72, market_regime: 'TREND_UP', strategy: 'Pullback', model_version: 'v2.1.0', reasoning_summary: 'Pullback to EMA50 support, RSI recovering from 42, volume increasing, bullish engulfing on 1H.', status: 'active', buy_probability: 71, sell_probability: 15, hold_probability: 14 },
  { signal_id: 'sig-003', symbol: 'SOL/USDT', timestamp: new Date(Date.now() - 10800000).toISOString(), timeframe: '4H', signal: 'HOLD', entry_price: 178.45, stop_loss: 172, take_profit: 195, risk_reward: 1.8, confidence: 45, market_regime: 'UNCERTAIN', strategy: 'Breakout', model_version: 'v2.1.0', reasoning_summary: 'Consolidation pattern, waiting for breakout confirmation. Volume declining, volatility contracting.', status: 'active', buy_probability: 35, sell_probability: 25, hold_probability: 40 },
  { signal_id: 'sig-004', symbol: 'BTC/USDT', timestamp: new Date(Date.now() - 14400000).toISOString(), timeframe: '1D', signal: 'SELL', entry_price: 68100, stop_loss: 69500, take_profit: 65000, risk_reward: 2.8, confidence: 81, market_regime: 'TREND_DOWN', strategy: 'Trend Following', model_version: 'v2.1.0', reasoning_summary: 'Bearish 1D trend, EMA20 below EMA50, RSI 38, declining volume, bearish divergence on MACD.', status: 'executed', buy_probability: 10, sell_probability: 78, hold_probability: 12 },
  { signal_id: 'sig-005', symbol: 'BNB/USDT', timestamp: new Date(Date.now() - 18000000).toISOString(), timeframe: '15M', signal: 'BUY', entry_price: 612, stop_loss: 605, take_profit: 628, risk_reward: 2.3, confidence: 68, market_regime: 'BREAKOUT', strategy: 'Breakout', model_version: 'v2.1.0', reasoning_summary: 'Breakout above resistance at $610, volume expansion 1.8x average, volatility expanding, closing confirmation.', status: 'active', buy_probability: 67, sell_probability: 18, hold_probability: 15 },
  { signal_id: 'sig-006', symbol: 'XRP/USDT', timestamp: new Date(Date.now() - 21600000).toISOString(), timeframe: '1H', signal: 'HOLD', entry_price: 0.6234, stop_loss: 0.615, take_profit: 0.645, risk_reward: 1.9, confidence: 52, market_regime: 'RANGE', strategy: 'Mean Reversion', model_version: 'v2.1.0', reasoning_summary: 'Price at range support, RSI 35, but volume declining. Waiting for confirmation.', status: 'expired', buy_probability: 40, sell_probability: 20, hold_probability: 40 },
];

export default function Signals() {
  const [search, setSearch] = useState('');
  const [signalFilter, setSignalFilter] = useState<string>('all');
  const [strategyFilter, setStrategyFilter] = useState<string>('all');
  const [minConfidence, setMinConfidence] = useState(0);

  const filteredSignals = demoSigs.filter((s) => {
    if (search && !s.symbol.toLowerCase().includes(search.toLowerCase())) return false;
    if (signalFilter !== 'all' && s.signal !== signalFilter) return false;
    if (strategyFilter !== 'all' && s.strategy !== strategyFilter) return false;
    if (s.confidence < minConfidence) return false;
    return true;
  });

  const strategies = [...new Set(demoSigs.map((s) => s.strategy))];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">AI Signals</h1>
          <p className="text-sm text-slate-400">Searchable signal feed with AI analysis</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Brain className="h-4 w-4" />
          <span>{filteredSignals.length} signals</span>
        </div>
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
              placeholder="Search by symbol..."
              className="w-full rounded-lg border border-slate-700 bg-slate-900/50 pl-10 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={signalFilter}
              onChange={(e) => setSignalFilter(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
            >
              <option value="all">All Signals</option>
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
              <option value="HOLD">HOLD</option>
            </select>
            <select
              value={strategyFilter}
              onChange={(e) => setStrategyFilter(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
            >
              <option value="all">All Strategies</option>
              {strategies.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
            <div className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2">
              <span className="text-xs text-slate-400">Min Conf:</span>
              <input
                type="number"
                value={minConfidence}
                onChange={(e) => setMinConfidence(Number(e.target.value))}
                min={0}
                max={100}
                className="w-12 bg-transparent text-sm text-white focus:outline-none"
              />
              <span className="text-xs text-slate-400">%</span>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Signal Cards */}
      {filteredSignals.length === 0 ? (
        <EmptyState
          icon={<Brain className="h-8 w-8" />}
          title="No signals match your current confidence threshold"
          description="Try adjusting your filters or lowering the minimum confidence requirement."
        />
      ) : (
        <div className="space-y-3">
          {filteredSignals.map((signal, i) => (
            <motion.div
              key={signal.signal_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: i * 0.05 }}
            >
              <GlassCard className="p-4" hover>
                <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                  {/* Signal Info */}
                  <div className="flex items-center gap-4 flex-1">
                    <div className="flex flex-col items-center">
                      <StatusBadge status={signal.signal} size="lg" />
                      <span className="mt-1 text-[10px] text-slate-500">{signal.timeframe}</span>
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-bold text-white">{signal.symbol}</h3>
                        <span className="text-xs text-slate-500">{signal.strategy}</span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {new Date(signal.timestamp).toLocaleString()} • Model {signal.model_version}
                      </p>
                    </div>
                  </div>

                  {/* Probabilities */}
                  <div className="flex items-center gap-4">
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Entry</p>
                      <p className="text-sm font-bold text-white">${signal.entry_price.toLocaleString()}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Stop</p>
                      <p className="text-sm font-bold text-red-400">${signal.stop_loss.toLocaleString()}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">Target</p>
                      <p className="text-sm font-bold text-emerald-400">${signal.take_profit.toLocaleString()}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500">R:R</p>
                      <p className="text-sm font-bold text-white">1:{signal.risk_reward}</p>
                    </div>
                  </div>

                  {/* Confidence */}
                  <div className="w-full lg:w-40">
                    <ConfidenceMeter value={signal.confidence} size="sm" />
                  </div>

                  {/* Regime & Status */}
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-medium text-cyan-400 bg-cyan-500/10 px-2 py-1 rounded">
                      {signal.market_regime}
                    </span>
                    <span className={`text-xs font-medium px-2 py-1 rounded ${
                      signal.status === 'active' ? 'bg-emerald-500/10 text-emerald-400' :
                      signal.status === 'executed' ? 'bg-blue-500/10 text-blue-400' :
                      'bg-slate-500/10 text-slate-400'
                    }`}>
                      {signal.status}
                    </span>
                  </div>
                </div>

                {/* Reasoning */}
                <div className="mt-3 pt-3 border-t border-slate-800/50">
                  <p className="text-xs text-slate-400">{signal.reasoning_summary}</p>
                </div>

                {/* Probability Bars */}
                <div className="mt-3 grid grid-cols-3 gap-2">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 rounded-full bg-slate-800">
                      <div className="h-full rounded-full bg-emerald-500" style={{ width: `${signal.buy_probability}%` }} />
                    </div>
                    <span className="text-[10px] text-emerald-400 w-8">{signal.buy_probability}%</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 rounded-full bg-slate-800">
                      <div className="h-full rounded-full bg-red-500" style={{ width: `${signal.sell_probability}%` }} />
                    </div>
                    <span className="text-[10px] text-red-400 w-8">{signal.sell_probability}%</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 rounded-full bg-slate-800">
                      <div className="h-full rounded-full bg-amber-500" style={{ width: `${signal.hold_probability}%` }} />
                    </div>
                    <span className="text-[10px] text-amber-400 w-8">{signal.hold_probability}%</span>
                  </div>
                </div>
              </GlassCard>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
