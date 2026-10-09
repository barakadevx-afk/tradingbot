import { useState } from 'react';
import {
  Brain,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import CandlestickChart from '../components/CandlestickChart';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import ConfidenceMeter from '../components/ConfidenceMeter';
import type { Market, Signal } from '../types';

const markets: Market[] = [
  { symbol: 'BTC/USDT', base: 'BTC', quote: 'USDT', price: 67432.50, change_24h: 2.34, volume_24h: 28500000000, high_24h: 68100, low_24h: 65800, bid: 67430, ask: 67435, spread: 5, spread_percent: 0.007, liquidity_score: 95, volatility: 0.023, is_enabled: true, asset_class: 'crypto', exchange: 'Binance' },
  { symbol: 'ETH/USDT', base: 'ETH', quote: 'USDT', price: 3542.80, change_24h: 1.87, volume_24h: 15200000000, high_24h: 3580, low_24h: 3460, bid: 3542.50, ask: 3543.10, spread: 0.60, spread_percent: 0.017, liquidity_score: 92, volatility: 0.028, is_enabled: true, asset_class: 'crypto', exchange: 'Binance' },
  { symbol: 'SOL/USDT', base: 'SOL', quote: 'USDT', price: 178.45, change_24h: -0.92, volume_24h: 3800000000, high_24h: 182, low_24h: 174, bid: 178.40, ask: 178.50, spread: 0.10, spread_percent: 0.056, liquidity_score: 88, volatility: 0.035, is_enabled: true, asset_class: 'crypto', exchange: 'Binance' },
  { symbol: 'BNB/USDT', base: 'BNB', quote: 'USDT', price: 612.30, change_24h: 0.56, volume_24h: 1900000000, high_24h: 618, low_24h: 605, bid: 612.25, ask: 612.35, spread: 0.10, spread_percent: 0.016, liquidity_score: 90, volatility: 0.021, is_enabled: true, asset_class: 'crypto', exchange: 'Binance' },
  { symbol: 'XRP/USDT', base: 'XRP', quote: 'USDT', price: 0.6234, change_24h: -1.23, volume_24h: 1200000000, high_24h: 0.635, low_24h: 0.615, bid: 0.6232, ask: 0.6236, spread: 0.0004, spread_percent: 0.064, liquidity_score: 85, volatility: 0.032, is_enabled: true, asset_class: 'crypto', exchange: 'Binance' },
  { symbol: 'ADA/USDT', base: 'ADA', quote: 'USDT', price: 0.4521, change_24h: 0.78, volume_24h: 450000000, high_24h: 0.458, low_24h: 0.442, bid: 0.4519, ask: 0.4523, spread: 0.0004, spread_percent: 0.088, liquidity_score: 78, volatility: 0.038, is_enabled: true, asset_class: 'crypto', exchange: 'Binance' },
  { symbol: 'DOGE/USDT', base: 'DOGE', quote: 'USDT', price: 0.1234, change_24h: -2.15, volume_24h: 890000000, high_24h: 0.127, low_24h: 0.121, bid: 0.1233, ask: 0.1235, spread: 0.0002, spread_percent: 0.162, liquidity_score: 75, volatility: 0.045, is_enabled: true, asset_class: 'crypto', exchange: 'Binance' },
];

const currentSignal: Signal = {
  signal_id: 'sig-btc-001',
  symbol: 'BTC/USDT',
  timestamp: new Date().toISOString(),
  timeframe: '4H',
  signal: 'BUY',
  entry_price: 67432,
  stop_loss: 66200,
  take_profit: 70500,
  risk_reward: 2.4,
  confidence: 78,
  market_regime: 'TREND_UP',
  strategy: 'Trend Following',
  model_version: 'v2.1.0',
  reasoning_summary: 'Bullish 4H trend, EMA20 above EMA50, RSI 61, rising volume, ATR within acceptable range, BUY probability 76%, risk/reward 1:2.4.',
  status: 'active',
  buy_probability: 76,
  sell_probability: 12,
  hold_probability: 12,
};

const timeframes = ['5M', '15M', '1H', '4H', '1D'];

export default function Trading() {
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [selectedTimeframe, setSelectedTimeframe] = useState('4H');
  const market = markets.find((m) => m.symbol === selectedSymbol) || markets[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Trading</h1>
          <p className="text-sm text-slate-400">Professional trading interface with AI analysis</p>
        </div>
        <div className="flex items-center gap-2">
          {timeframes.map((tf) => (
            <button
              key={tf}
              onClick={() => setSelectedTimeframe(tf)}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                selectedTimeframe === tf
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Market List */}
        <div className="lg:col-span-2">
          <GlassCard className="p-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 px-2 mb-2">Markets</h3>
            <div className="space-y-1">
              {markets.map((m) => (
                <button
                  key={m.symbol}
                  onClick={() => setSelectedSymbol(m.symbol)}
                  className={`w-full flex items-center gap-2 rounded-lg px-2 py-2 text-left transition-colors ${
                    selectedSymbol === m.symbol
                      ? 'bg-emerald-500/10 border border-emerald-500/20'
                      : 'hover:bg-slate-800/50'
                  }`}
                >
                  <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-800 text-[10px] font-bold text-slate-300">
                    {m.base.charAt(0)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-white truncate">{m.base}</p>
                    <p className={`text-[10px] font-semibold ${m.change_24h >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {m.change_24h >= 0 ? '+' : ''}{m.change_24h.toFixed(2)}%
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </GlassCard>
        </div>

        {/* Chart */}
        <div className="lg:col-span-7">
          <GlassCard className="p-4">
            {/* Chart Header */}
            <div className="flex flex-wrap items-center gap-4 mb-4">
              <div>
                <h2 className="text-xl font-bold text-white">{selectedSymbol}</h2>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-white">
                    ${market.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </span>
                  <span className={`flex items-center gap-0.5 text-sm font-semibold ${
                    market.change_24h >= 0 ? 'text-emerald-400' : 'text-red-400'
                  }`}>
                    {market.change_24h >= 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
                    {market.change_24h >= 0 ? '+' : ''}{market.change_24h.toFixed(2)}%
                  </span>
                </div>
              </div>
              <div className="ml-auto flex items-center gap-4 text-xs">
                <div className="text-center">
                  <p className="text-slate-500">24h High</p>
                  <p className="font-semibold text-white">${market.high_24h.toLocaleString()}</p>
                </div>
                <div className="text-center">
                  <p className="text-slate-500">24h Low</p>
                  <p className="font-semibold text-white">${market.low_24h.toLocaleString()}</p>
                </div>
                <div className="text-center">
                  <p className="text-slate-500">Volume</p>
                  <p className="font-semibold text-white">${(market.volume_24h / 1e9).toFixed(1)}B</p>
                </div>
              </div>
            </div>

            {/* Candlestick Chart */}
            <CandlestickChart symbol={selectedSymbol} timeframe={selectedTimeframe} />

            {/* Bid/Ask */}
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="rounded-lg bg-emerald-500/5 border border-emerald-500/10 p-3">
                <p className="text-xs text-slate-500 mb-1">Best Bid</p>
                <p className="text-lg font-bold text-emerald-400">${market.bid.toLocaleString()}</p>
              </div>
              <div className="rounded-lg bg-red-500/5 border border-red-500/10 p-3">
                <p className="text-xs text-slate-500 mb-1">Best Ask</p>
                <p className="text-lg font-bold text-red-400">${market.ask.toLocaleString()}</p>
              </div>
            </div>
          </GlassCard>
        </div>

        {/* AI Analysis Panel */}
        <div className="lg:col-span-3 space-y-4">
          <GlassCard className="p-4">
            <div className="flex items-center gap-2 mb-4">
              <Brain className="h-5 w-5 text-cyan-400" />
              <h3 className="text-sm font-semibold text-white">AI Analysis</h3>
            </div>

            {/* Signal */}
            <div className="text-center mb-4">
              <StatusBadge status={currentSignal.signal} size="lg" />
              <p className="mt-2 text-xs text-slate-500">{currentSignal.strategy}</p>
            </div>

            {/* Probabilities */}
            <div className="space-y-3 mb-4">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-emerald-400 font-medium">BUY</span>
                  <span className="text-emerald-400 font-bold">{currentSignal.buy_probability}%</span>
                </div>
                <div className="h-2 rounded-full bg-slate-800">
                  <div className="h-full rounded-full bg-emerald-500" style={{ width: `${currentSignal.buy_probability}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-red-400 font-medium">SELL</span>
                  <span className="text-red-400 font-bold">{currentSignal.sell_probability}%</span>
                </div>
                <div className="h-2 rounded-full bg-slate-800">
                  <div className="h-full rounded-full bg-red-500" style={{ width: `${currentSignal.sell_probability}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-amber-400 font-medium">HOLD</span>
                  <span className="text-amber-400 font-bold">{currentSignal.hold_probability}%</span>
                </div>
                <div className="h-2 rounded-full bg-slate-800">
                  <div className="h-full rounded-full bg-amber-500" style={{ width: `${currentSignal.hold_probability}%` }} />
                </div>
              </div>
            </div>

            {/* Confidence */}
            <ConfidenceMeter value={currentSignal.confidence} label="AI Confidence" size="md" />

            {/* Regime */}
            <div className="mt-4 pt-3 border-t border-slate-800">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400">Market Regime</span>
                <span className="font-semibold text-cyan-400">{currentSignal.market_regime}</span>
              </div>
            </div>
          </GlassCard>

          {/* Trade Setup */}
          <GlassCard className="p-4">
            <h3 className="text-sm font-semibold text-white mb-3">Trade Setup</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-400">Entry</span>
                <span className="font-semibold text-white">${currentSignal.entry_price.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Stop Loss</span>
                <span className="font-semibold text-red-400">${currentSignal.stop_loss.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Take Profit</span>
                <span className="font-semibold text-emerald-400">${currentSignal.take_profit.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Risk/Reward</span>
                <span className="font-semibold text-white">1:{currentSignal.risk_reward}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Position Size</span>
                <span className="font-semibold text-white">0.029 BTC</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Risk Amount</span>
                <span className="font-semibold text-amber-400">$50.00</span>
              </div>
            </div>
          </GlassCard>

          {/* Reasoning */}
          <GlassCard className="p-4">
            <h3 className="text-sm font-semibold text-white mb-2">AI Reasoning</h3>
            <p className="text-xs text-slate-400 leading-relaxed">{currentSignal.reasoning_summary}</p>
          </GlassCard>
        </div>
      </div>

      {/* Bottom Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Open Positions */}
        <GlassCard className="p-4">
          <h3 className="text-sm font-semibold text-white mb-3">Open Positions</h3>
          <div className="space-y-2">
            <div className="rounded-lg bg-slate-800/30 p-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-white">BTC/USDT</p>
                  <p className="text-xs text-slate-500">Long • 0.029 BTC</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-emerald-400">+$45.20</p>
                  <p className="text-xs text-slate-500">+1.52%</p>
                </div>
              </div>
            </div>
            <div className="rounded-lg bg-slate-800/30 p-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-white">ETH/USDT</p>
                  <p className="text-xs text-slate-500">Long • 0.23 ETH</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-emerald-400">+$28.50</p>
                  <p className="text-xs text-slate-500">+0.89%</p>
                </div>
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Pending Orders */}
        <GlassCard className="p-4">
          <h3 className="text-sm font-semibold text-white mb-3">Pending Orders</h3>
          <div className="space-y-2">
            <div className="rounded-lg bg-slate-800/30 p-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-white">SOL/USDT</p>
                  <p className="text-xs text-slate-500">Limit Buy • 5.6 SOL</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-white">$175.00</p>
                  <p className="text-xs text-amber-400">Pending</p>
                </div>
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Recent Trades */}
        <GlassCard className="p-4">
          <h3 className="text-sm font-semibold text-white mb-3">Recent Trades</h3>
          <div className="space-y-2">
            <div className="rounded-lg bg-slate-800/30 p-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-white">BTC/USDT</p>
                  <p className="text-xs text-slate-500">Long • Closed 2h ago</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-emerald-400">+$67.80</p>
                  <p className="text-xs text-slate-500">+2.3%</p>
                </div>
              </div>
            </div>
            <div className="rounded-lg bg-slate-800/30 p-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-white">ETH/USDT</p>
                  <p className="text-xs text-slate-500">Long • Closed 5h ago</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-semibold text-red-400">-$12.40</p>
                  <p className="text-xs text-slate-500">-0.4%</p>
                </div>
              </div>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
