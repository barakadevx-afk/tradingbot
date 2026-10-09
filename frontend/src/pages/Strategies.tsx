import { useState } from 'react';
import { motion } from 'framer-motion';
import { Layers, Play, Pause, Copy, Settings } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import type { Strategy } from '../types';

const demoStrategies: Strategy[] = [
  { id: 'strat-001', name: 'Trend Following', status: 'active', markets: ['BTC/USDT', 'ETH/USDT', 'SOL/USDT'], timeframes: ['4H', '1D'], ai_model: 'BARAKA Trend Predictor v2.1.0', performance: 18.2, risk_profile: 'moderate', created_at: '2024-01-15', parameters: { ema_fast: 20, ema_slow: 50, atr_period: 14, risk_per_trade: 0.5 } },
  { id: 'strat-002', name: 'Breakout', status: 'active', markets: ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'], timeframes: ['15M', '1H'], ai_model: 'BARAKA Breakout v1.0.0', performance: 12.5, risk_profile: 'aggressive', created_at: '2024-02-20', parameters: { consolidation_periods: 20, volume_multiplier: 1.5, atr_stop: 2.0 } },
  { id: 'strat-003', name: 'Pullback', status: 'active', markets: ['BTC/USDT', 'ETH/USDT'], timeframes: ['1H', '4H'], ai_model: 'BARAKA Trend Predictor v2.1.0', performance: 8.7, risk_profile: 'conservative', created_at: '2024-03-10', parameters: { ema_pullback: 50, rsi_min: 40, rsi_max: 60, risk_per_trade: 0.5 } },
  { id: 'strat-004', name: 'Mean Reversion', status: 'inactive', markets: ['BTC/USDT', 'XRP/USDT', 'ADA/USDT'], timeframes: ['1H', '4H'], ai_model: 'BARAKA Range Detector v1.2.0', performance: -2.1, risk_profile: 'conservative', created_at: '2024-04-05', parameters: { bb_period: 20, bb_std: 2, rsi_oversold: 30, rsi_overbought: 70 } },
  { id: 'strat-005', name: 'SMA Crossover', status: 'backtesting', markets: ['BTC/USDT'], timeframes: ['1D'], ai_model: 'None', performance: 5.3, risk_profile: 'moderate', created_at: '2024-05-12', parameters: { sma_fast: 50, sma_slow: 200 } },
];

export default function Strategies() {
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Strategies</h1>
          <p className="text-sm text-slate-400">Manage trading strategies and their configurations</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-400 transition-colors">
          <Layers className="h-4 w-4" />
          New Strategy
        </button>
      </div>

      <div className="space-y-3">
        {demoStrategies.map((strategy, i) => (
          <motion.div
            key={strategy.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <GlassCard className="p-4" hover>
              <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                <div className="flex items-center gap-3 flex-1">
                  <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${
                    strategy.status === 'active' ? 'bg-emerald-500/10 text-emerald-400' :
                    strategy.status === 'backtesting' ? 'bg-blue-500/10 text-blue-400' :
                    'bg-slate-800 text-slate-500'
                  }`}>
                    {strategy.status === 'active' ? <Play className="h-5 w-5" /> :
                     strategy.status === 'backtesting' ? <Settings className="h-5 w-5" /> :
                     <Pause className="h-5 w-5" />}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-bold text-white">{strategy.name}</h3>
                      <StatusBadge status={strategy.status} size="sm" />
                    </div>
                    <p className="text-xs text-slate-500">
                      {strategy.markets.join(', ')} • {strategy.timeframes.join(', ')}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-6 text-sm">
                  <div className="text-center">
                    <p className="text-xs text-slate-500">AI Model</p>
                    <p className="font-semibold text-white text-xs">{strategy.ai_model.split(' ')[0]}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-slate-500">Performance</p>
                    <p className={`font-bold ${strategy.performance >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {strategy.performance >= 0 ? '+' : ''}{strategy.performance}%
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-slate-500">Risk</p>
                    <p className={`font-semibold ${
                      strategy.risk_profile === 'conservative' ? 'text-emerald-400' :
                      strategy.risk_profile === 'moderate' ? 'text-amber-400' : 'text-red-400'
                    }`}>
                      {strategy.risk_profile}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setSelectedStrategy(strategy)}
                    className="rounded-lg border border-slate-700 p-2 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                    title="View Details"
                  >
                    <Settings className="h-4 w-4" />
                  </button>
                  <button className="rounded-lg border border-slate-700 p-2 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors" title="Clone">
                    <Copy className="h-4 w-4" />
                  </button>
                  {strategy.status === 'active' ? (
                    <button className="rounded-lg border border-red-500/30 p-2 text-red-400 hover:bg-red-500/10 transition-colors" title="Disable">
                      <Pause className="h-4 w-4" />
                    </button>
                  ) : (
                    <button className="rounded-lg border border-emerald-500/30 p-2 text-emerald-400 hover:bg-emerald-500/10 transition-colors" title="Enable">
                      <Play className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* Strategy Detail Modal */}
      {selectedStrategy && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">{selectedStrategy.name}</h2>
              <StatusBadge status={selectedStrategy.status} />
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-white mb-2">Markets</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedStrategy.markets.map((m) => (
                    <span key={m} className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">{m}</span>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-2">Timeframes</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedStrategy.timeframes.map((tf) => (
                    <span key={tf} className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">{tf}</span>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white mb-2">Parameters</h3>
                <div className="rounded-lg bg-slate-800/50 p-3 space-y-1">
                  {Object.entries(selectedStrategy.parameters).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-slate-400">{key}</span>
                      <span className="font-mono text-white">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedStrategy(null)}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
              >
                Close
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
