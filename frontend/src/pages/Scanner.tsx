import { motion } from 'framer-motion';
import { Radar, ArrowUpRight, ArrowDownRight, Minus, AlertCircle } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import ConfidenceMeter from '../components/ConfidenceMeter';
import EmptyState from '../components/EmptyState';

const opportunities = [
  { symbol: 'BTC/USDT', signal: 'BUY', confidence: 78, risk_reward: 2.4, liquidity: 95, trend: 85, regime: 'TREND_UP', regime_quality: 90, volatility: 'normal', score: 82 },
  { symbol: 'ETH/USDT', signal: 'BUY', confidence: 72, risk_reward: 2.1, liquidity: 92, trend: 78, regime: 'TREND_UP', regime_quality: 85, volatility: 'normal', score: 76 },
  { symbol: 'BNB/USDT', signal: 'BUY', confidence: 68, risk_reward: 2.3, liquidity: 90, trend: 72, regime: 'BREAKOUT', regime_quality: 75, volatility: 'expanding', score: 71 },
  { symbol: 'BTC/USDT', signal: 'SELL', confidence: 81, risk_reward: 2.8, liquidity: 95, trend: 88, regime: 'TREND_DOWN', regime_quality: 92, volatility: 'normal', score: 80 },
  { symbol: 'SOL/USDT', signal: 'HOLD', confidence: 45, risk_reward: 1.8, liquidity: 88, trend: 40, regime: 'UNCERTAIN', regime_quality: 30, volatility: 'contracting', score: 35 },
];

export default function Scanner() {
  const buySetups = opportunities.filter((o) => o.signal === 'BUY' && o.score >= 70);
  const sellSetups = opportunities.filter((o) => o.signal === 'SELL' && o.score >= 70);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Market Scanner</h1>
        <p className="text-sm text-slate-400">Scan all enabled symbols for high-quality opportunities</p>
      </div>

      {/* Top Opportunities */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <GlassCard className="p-4" glow="emerald">
          <div className="flex items-center gap-2 mb-3">
            <ArrowUpRight className="h-5 w-5 text-emerald-400" />
            <h2 className="text-sm font-semibold text-white">Best BUY Setup</h2>
          </div>
          {buySetups.length > 0 ? (
            <div className="space-y-2">
              {buySetups.sort((a, b) => b.score - a.score)[0] && (
                <div className="rounded-lg bg-emerald-500/5 border border-emerald-500/10 p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-lg font-bold text-white">{buySetups.sort((a, b) => b.score - a.score)[0].symbol}</span>
                    <span className="text-lg font-bold text-emerald-400">Score: {buySetups.sort((a, b) => b.score - a.score)[0].score}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Confidence</span>
                      <span className="text-white font-semibold">{buySetups.sort((a, b) => b.score - a.score)[0].confidence}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">R:R</span>
                      <span className="text-white font-semibold">1:{buySetups.sort((a, b) => b.score - a.score)[0].risk_reward}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Trend</span>
                      <span className="text-white font-semibold">{buySetups.sort((a, b) => b.score - a.score)[0].trend}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Regime</span>
                      <span className="text-cyan-400 font-semibold">{buySetups.sort((a, b) => b.score - a.score)[0].regime}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-slate-500">No high-quality BUY setup detected.</p>
          )}
        </GlassCard>

        <GlassCard className="p-4" glow="red">
          <div className="flex items-center gap-2 mb-3">
            <ArrowDownRight className="h-5 w-5 text-red-400" />
            <h2 className="text-sm font-semibold text-white">Best SELL Setup</h2>
          </div>
          {sellSetups.length > 0 ? (
            <div className="space-y-2">
              {sellSetups.sort((a, b) => b.score - a.score)[0] && (
                <div className="rounded-lg bg-red-500/5 border border-red-500/10 p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-lg font-bold text-white">{sellSetups.sort((a, b) => b.score - a.score)[0].symbol}</span>
                    <span className="text-lg font-bold text-red-400">Score: {sellSetups.sort((a, b) => b.score - a.score)[0].score}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Confidence</span>
                      <span className="text-white font-semibold">{sellSetups.sort((a, b) => b.score - a.score)[0].confidence}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">R:R</span>
                      <span className="text-white font-semibold">1:{sellSetups.sort((a, b) => b.score - a.score)[0].risk_reward}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Trend</span>
                      <span className="text-white font-semibold">{sellSetups.sort((a, b) => b.score - a.score)[0].trend}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Regime</span>
                      <span className="text-cyan-400 font-semibold">{sellSetups.sort((a, b) => b.score - a.score)[0].regime}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-slate-500">No high-quality SELL setup detected.</p>
          )}
        </GlassCard>
      </div>

      {/* All Opportunities */}
      <GlassCard className="p-6">
        <h2 className="text-lg font-semibold text-white mb-4">All Scanned Opportunities</h2>
        {opportunities.filter((o) => o.score >= 70).length === 0 ? (
          <EmptyState
            icon={<AlertCircle className="h-8 w-8" />}
            title="No high-quality opportunity currently detected"
            description="The scanner continuously monitors all enabled symbols. Opportunities will appear when conditions meet the threshold."
          />
        ) : (
          <div className="space-y-3">
            {opportunities.sort((a, b) => b.score - a.score).map((opp, i) => (
              <motion.div
                key={opp.symbol + opp.signal}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className={`rounded-lg border p-4 ${
                  opp.score >= 70
                    ? 'border-slate-700/50 bg-slate-800/30'
                    : 'border-slate-800/30 bg-slate-900/20 opacity-60'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                  <div className="flex items-center gap-3 flex-1">
                    <StatusBadge status={opp.signal} />
                    <div>
                      <h3 className="text-sm font-bold text-white">{opp.symbol}</h3>
                      <p className="text-xs text-slate-500">{opp.regime} • {opp.volatility} volatility</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <div className="text-center">
                      <p className="text-slate-500">Confidence</p>
                      <p className="font-semibold text-white">{opp.confidence}%</p>
                    </div>
                    <div className="text-center">
                      <p className="text-slate-500">R:R</p>
                      <p className="font-semibold text-white">1:{opp.risk_reward}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-slate-500">Liquidity</p>
                      <p className="font-semibold text-white">{opp.liquidity}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-slate-500">Trend</p>
                      <p className="font-semibold text-white">{opp.trend}%</p>
                    </div>
                    <div className="w-24">
                      <ConfidenceMeter value={opp.score} size="sm" label="Score" />
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </GlassCard>
    </div>
  );
}
