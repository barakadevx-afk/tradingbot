import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Briefcase,
  TrendingUp,
  TrendingDown,
  Target,
  Shield,
  Activity,
  Brain,
  ArrowUpRight,
  ArrowDownRight,
  AlertTriangle,
  Zap,
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { useTradingStore } from '../store/tradingStore';
import { useAuthStore } from '../store/authStore';
import MetricCard from '../components/MetricCard';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import ConfidenceMeter from '../components/ConfidenceMeter';
import LoadingSkeleton, { CardSkeleton } from '../components/LoadingSkeleton';
import type { Market, Portfolio, Signal } from '../types';

// Generate realistic demo equity curve
function generateEquityCurve(baseValue: number, days: number = 30) {
  const data = [];
  let value = baseValue;
  const now = Date.now();
  for (let i = days; i >= 0; i--) {
    const date = new Date(now - i * 24 * 60 * 60 * 1000);
    value = value * (1 + (Math.random() - 0.48) * 0.02);
    data.push({
      timestamp: date.toISOString().split('T')[0],
      value: Math.round(value * 100) / 100,
    });
  }
  return data;
}

const demoMarkets: Market[] = [
  { symbol: 'BTC/USDT', base: 'BTC', quote: 'USDT', price: 67432.50, change_24h: 2.34, volume_24h: 28500000000, high_24h: 68100, low_24h: 65800, bid: 67430, ask: 67435, spread: 5, spread_percent: 0.007, liquidity_score: 95, volatility: 0.023, is_enabled: true },
  { symbol: 'ETH/USDT', base: 'ETH', quote: 'USDT', price: 3542.80, change_24h: 1.87, volume_24h: 15200000000, high_24h: 3580, low_24h: 3460, bid: 3542.50, ask: 3543.10, spread: 0.60, spread_percent: 0.017, liquidity_score: 92, volatility: 0.028, is_enabled: true },
  { symbol: 'SOL/USDT', base: 'SOL', quote: 'USDT', price: 178.45, change_24h: -0.92, volume_24h: 3800000000, high_24h: 182, low_24h: 174, bid: 178.40, ask: 178.50, spread: 0.10, spread_percent: 0.056, liquidity_score: 88, volatility: 0.035, is_enabled: true },
  { symbol: 'BNB/USDT', base: 'BNB', quote: 'USDT', price: 612.30, change_24h: 0.56, volume_24h: 1900000000, high_24h: 618, low_24h: 605, bid: 612.25, ask: 612.35, spread: 0.10, spread_percent: 0.016, liquidity_score: 90, volatility: 0.021, is_enabled: true },
  { symbol: 'XRP/USDT', base: 'XRP', quote: 'USDT', price: 0.6234, change_24h: -1.23, volume_24h: 1200000000, high_24h: 0.635, low_24h: 0.615, bid: 0.6232, ask: 0.6236, spread: 0.0004, spread_percent: 0.064, liquidity_score: 85, volatility: 0.032, is_enabled: true },
];

const demoTrends: Signal[] = [
  { signal_id: 'sig-001', symbol: 'BTC/USDT', timestamp: new Date().toISOString(), timeframe: '4H', signal: 'BUY', entry_price: 67432, stop_loss: 66200, take_profit: 70500, risk_reward: 2.4, confidence: 78, market_regime: 'TREND_UP', strategy: 'Trend Following', model_version: 'v2.1.0', reasoning_summary: 'Bullish 4H trend, EMA20 above EMA50, RSI 61, rising volume, ATR within acceptable range, BUY probability 76%, risk/reward 1:2.4.', status: 'active', buy_probability: 76, sell_probability: 12, hold_probability: 12 },
  { signal_id: 'sig-002', symbol: 'ETH/USDT', timestamp: new Date().toISOString(), timeframe: '1H', signal: 'BUY', entry_price: 3542, stop_loss: 3480, take_profit: 3680, risk_reward: 2.1, confidence: 72, market_regime: 'TREND_UP', strategy: 'Pullback', model_version: 'v2.1.0', reasoning_summary: 'Pullback to EMA50 support, RSI recovering from 42, volume increasing, bullish engulfing on 1H.', status: 'active', buy_probability: 71, sell_probability: 15, hold_probability: 14 },
  { signal_id: 'sig-003', symbol: 'SOL/USDT', timestamp: new Date().toISOString(), timeframe: '4H', signal: 'HOLD', entry_price: 178.45, stop_loss: 172, take_profit: 195, risk_reward: 1.8, confidence: 45, market_regime: 'UNCERTAIN', strategy: 'Breakout', model_version: 'v2.1.0', reasoning_summary: 'Consolidation pattern, waiting for breakout confirmation. Volume declining, volatility contracting.', status: 'active', buy_probability: 35, sell_probability: 25, hold_probability: 40 },
];

export default function Dashboard() {
  const { user } = useAuthStore();
  const { tradingMode, killSwitchActive } = useTradingStore();
  const [loading, setLoading] = useState(true);
  const [equityCurve] = useState(() => generateEquityCurve(10000));
  const [portfolio] = useState<Portfolio>({
    total_value: 10247.83,
    cash: 8247.83,
    open_exposure: 2000,
    realized_pnl: 147.83,
    unrealized_pnl: 100.00,
    total_pnl: 247.83,
    leverage: 1,
    drawdown: 0.012,
    daily_pnl: 87.50,
    weekly_pnl: 147.83,
    monthly_pnl: 247.83,
    equity_curve: equityCurve,
    allocation: [
      { symbol: 'USDT', value: 8247.83, percentage: 80.5 },
      { symbol: 'BTC', value: 1200, percentage: 11.7 },
      { symbol: 'ETH', value: 800, percentage: 7.8 },
    ],
  });

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 800);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <CardSkeleton />
          </div>
          <CardSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-slate-400">Welcome back, {user?.full_name || 'Trader'}</p>
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={tradingMode === 'paper' ? 'HOLD' : 'BUY'} size="lg" />
          {killSwitchActive && (
            <div className="flex items-center gap-2 rounded-lg bg-red-500/10 border border-red-500/20 px-3 py-2">
              <AlertTriangle className="h-4 w-4 text-red-400" />
              <span className="text-sm font-semibold text-red-400">Kill Switch Active</span>
            </div>
          )}
        </div>
      </div>

      {/* Demo Banner */}
      <div className="rounded-lg border border-amber-500/20 bg-amber-500/5 px-4 py-3 flex items-center gap-3">
        <Zap className="h-4 w-4 text-amber-400 flex-shrink-0" />
        <p className="text-sm text-amber-300">
          <span className="font-semibold">DEMO DATA</span> — Displaying simulated market data for demonstration purposes. No real funds at risk.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Portfolio Value"
          value={`$${portfolio.total_value.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
          change={2.48}
          changeLabel="all time"
          icon={<Briefcase className="h-4 w-4" />}
          trend="up"
        />
        <MetricCard
          title="Today's P&L"
          value={`+$${portfolio.daily_pnl.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
          change={0.87}
          changeLabel="today"
          icon={<TrendingUp className="h-4 w-4" />}
          trend="up"
        />
        <MetricCard
          title="Win Rate"
          value="62.5%"
          change={3.2}
          changeLabel="vs last week"
          icon={<Target className="h-4 w-4" />}
          trend="up"
        />
        <MetricCard
          title="Max Drawdown"
          value={`${(portfolio.drawdown * 100).toFixed(1)}%`}
          change={-0.3}
          changeLabel="current"
          icon={<Shield className="h-4 w-4" />}
          trend="down"
        />
      </div>

      {/* Charts and Markets */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Equity Curve */}
        <GlassCard className="lg:col-span-2 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-semibold text-white">Portfolio Equity</h2>
              <p className="text-xs text-slate-500">Last 30 days</p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-emerald-400">+$247.83</span>
              <span className="text-xs text-slate-500">(+2.48%)</span>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={equityCurve}>
                <defs>
                  <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="timestamp"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 10, fill: '#64748b' }}
                  tickFormatter={(val) => val.slice(5)}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 10, fill: '#64748b' }}
                  domain={['dataMin - 50', 'dataMax + 50']}
                  tickFormatter={(val) => `$${(val / 1000).toFixed(1)}k`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                  labelStyle={{ color: '#94a3b8' }}
                  formatter={(value: number) => [`$${value.toFixed(2)}`, 'Equity']}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#10b981"
                  strokeWidth={2}
                  fill="url(#equityGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* AI Confidence */}
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold text-white mb-4">AI Confidence</h2>
          <div className="space-y-5">
            <div>
              <ConfidenceMeter value={78} label="Overall Confidence" size="lg" />
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400">Trend Confirmation</span>
                <span className="font-semibold text-emerald-400">85%</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400">Momentum</span>
                <span className="font-semibold text-emerald-400">70%</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400">Liquidity Quality</span>
                <span className="font-semibold text-emerald-400">90%</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400">Regime Compatibility</span>
                <span className="font-semibold text-emerald-400">82%</span>
              </div>
            </div>
            <div className="pt-3 border-t border-slate-800">
              <div className="flex items-center gap-2 text-sm">
                <Brain className="h-4 w-4 text-cyan-400" />
                <span className="text-slate-300">Market Regime:</span>
                <span className="font-semibold text-cyan-400">TREND_UP</span>
              </div>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Market Overview */}
      <GlassCard className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Market Overview</h2>
          <span className="text-xs text-slate-500">Demo Data</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="pb-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Symbol</th>
                <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Price</th>
                <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">24h Change</th>
                <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Volume</th>
                <th className="pb-3 text-center text-xs font-medium uppercase tracking-wider text-slate-500">AI Signal</th>
                <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Confidence</th>
                <th className="pb-3 text-center text-xs font-medium uppercase tracking-wider text-slate-500">Regime</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {demoMarkets.map((market) => {
                const signal = demoTrends.find((s) => s.symbol === market.symbol);
                return (
                  <tr key={market.symbol} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3">
                      <div className="flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 text-xs font-bold text-slate-300">
                          {market.base.charAt(0)}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-white">{market.symbol}</p>
                          <p className="text-xs text-slate-500">{market.base}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 text-right">
                      <p className="text-sm font-semibold text-white">
                        ${market.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </p>
                    </td>
                    <td className="py-3 text-right">
                      <div className={`flex items-center justify-end gap-1 text-sm font-semibold ${
                        market.change_24h >= 0 ? 'text-emerald-400' : 'text-red-400'
                      }`}>
                        {market.change_24h >= 0 ? (
                          <ArrowUpRight className="h-3 w-3" />
                        ) : (
                          <ArrowDownRight className="h-3 w-3" />
                        )}
                        {market.change_24h >= 0 ? '+' : ''}{market.change_24h.toFixed(2)}%
                      </div>
                    </td>
                    <td className="py-3 text-right">
                      <p className="text-sm text-slate-400">
                        ${(market.volume_24h / 1e9).toFixed(1)}B
                      </p>
                    </td>
                    <td className="py-3 text-center">
                      {signal ? (
                        <StatusBadge status={signal.signal} size="sm" />
                      ) : (
                        <span className="text-xs text-slate-500">—</span>
                      )}
                    </td>
                    <td className="py-3 text-right">
                      {signal ? (
                        <span className="text-sm font-semibold text-white">{signal.confidence}%</span>
                      ) : (
                        <span className="text-xs text-slate-500">—</span>
                      )}
                    </td>
                    <td className="py-3 text-center">
                      <span className="text-xs font-medium text-cyan-400">
                        {signal?.market_regime || 'UNCERTAIN'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </GlassCard>

      {/* Recent Signals */}
      <GlassCard className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Recent AI Signals</h2>
          <span className="text-xs text-slate-500">{demoSignals.length} active</span>
        </div>
        <div className="space-y-3">
          {demoSignals.map((signal) => (
            <div
              key={signal.signal_id}
              className="flex flex-col sm:flex-row sm:items-center gap-3 rounded-lg border border-slate-800/50 bg-slate-800/20 p-4"
            >
              <div className="flex items-center gap-3 flex-1">
                <StatusBadge status={signal.signal} />
                <div>
                  <p className="text-sm font-semibold text-white">{signal.symbol}</p>
                  <p className="text-xs text-slate-500">{signal.strategy} • {signal.timeframe}</p>
                </div>
              </div>
              <div className="flex items-center gap-6 text-sm">
                <div className="text-right">
                  <p className="text-xs text-slate-500">Entry</p>
                  <p className="font-semibold text-white">${signal.entry_price.toLocaleString()}</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500">Confidence</p>
                  <p className="font-semibold text-emerald-400">{signal.confidence}%</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-slate-500">R:R</p>
                  <p className="font-semibold text-white">1:{signal.risk_reward}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
