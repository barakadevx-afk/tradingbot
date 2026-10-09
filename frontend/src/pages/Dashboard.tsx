import { useEffect, useState } from 'react';
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  BarChart3,
  BrainCircuit,
  BriefcaseBusiness,
  ChevronDown,
  CircleDollarSign,
  Clock3,
  ExternalLink,
  Gauge,
  Layers3,
  ShieldCheck,
  Sparkles,
  Wallet,
  Zap,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useTradingStore } from '../store/tradingStore';
import { useAuthStore } from '../store/authStore';
import CandlestickChart from '../components/CandlestickChart';
import StatusBadge from '../components/StatusBadge';
import { CardSkeleton } from '../components/LoadingSkeleton';
import type { Market, Signal } from '../types';

const demoMarkets: Market[] = [
  { symbol: 'BTC/USDT', base: 'BTC', quote: 'USDT', price: 67432.50, change_24h: 2.34, volume_24h: 28500000000, high_24h: 68100, low_24h: 65800, bid: 67430, ask: 67435, spread: 5, spread_percent: 0.007, liquidity_score: 95, volatility: 0.023, is_enabled: true, asset_class: 'crypto', exchange: 'Binance' },
  { symbol: 'ETH/USDT', base: 'ETH', quote: 'USDT', price: 3542.80, change_24h: 1.87, volume_24h: 15200000000, high_24h: 3580, low_24h: 3460, bid: 3542.50, ask: 3543.10, spread: 0.60, spread_percent: 0.017, liquidity_score: 92, volatility: 0.028, is_enabled: true, asset_class: 'crypto', exchange: 'Binance' },
  { symbol: 'SOL/USDT', base: 'SOL', quote: 'USDT', price: 178.45, change_24h: -0.92, volume_24h: 3800000000, high_24h: 182, low_24h: 174, bid: 178.40, ask: 178.50, spread: 0.10, spread_percent: 0.056, liquidity_score: 88, volatility: 0.035, is_enabled: true, asset_class: 'crypto', exchange: 'Binance' },
  { symbol: 'BNB/USDT', base: 'BNB', quote: 'USDT', price: 612.30, change_24h: 0.56, volume_24h: 1900000000, high_24h: 618, low_24h: 605, bid: 612.25, ask: 612.35, spread: 0.10, spread_percent: 0.016, liquidity_score: 90, volatility: 0.021, is_enabled: true, asset_class: 'crypto', exchange: 'Binance' },
  { symbol: 'XRP/USDT', base: 'XRP', quote: 'USDT', price: 0.6234, change_24h: -1.23, volume_24h: 1200000000, high_24h: 0.635, low_24h: 0.615, bid: 0.6232, ask: 0.6236, spread: 0.0004, spread_percent: 0.064, liquidity_score: 85, volatility: 0.032, is_enabled: true, asset_class: 'crypto', exchange: 'Binance' },
];

const demoSignals: Signal[] = [
  { signal_id: 'sig-001', symbol: 'BTC/USDT', timestamp: new Date().toISOString(), timeframe: '4H', signal: 'BUY', entry_price: 67432, stop_loss: 66200, take_profit: 70500, risk_reward: 2.4, confidence: 78, market_regime: 'TREND_UP', strategy: 'Trend Following', model_version: 'v2.1.0', reasoning_summary: 'Bullish 4H trend, EMA20 above EMA50, RSI 61, rising volume, ATR within acceptable range, BUY probability 76%, risk/reward 1:2.4.', status: 'active', buy_probability: 76, sell_probability: 12, hold_probability: 12 },
  { signal_id: 'sig-002', symbol: 'ETH/USDT', timestamp: new Date().toISOString(), timeframe: '1H', signal: 'BUY', entry_price: 3542, stop_loss: 3480, take_profit: 3680, risk_reward: 2.1, confidence: 72, market_regime: 'TREND_UP', strategy: 'Pullback', model_version: 'v2.1.0', reasoning_summary: 'Pullback to EMA50 support, RSI recovering from 42, volume increasing, bullish engulfing on 1H.', status: 'active', buy_probability: 71, sell_probability: 15, hold_probability: 14 },
  { signal_id: 'sig-003', symbol: 'SOL/USDT', timestamp: new Date().toISOString(), timeframe: '4H', signal: 'HOLD', entry_price: 178.45, stop_loss: 172, take_profit: 195, risk_reward: 1.8, confidence: 45, market_regime: 'UNCERTAIN', strategy: 'Breakout', model_version: 'v2.1.0', reasoning_summary: 'Consolidation pattern, waiting for breakout confirmation. Volume declining, volatility contracting.', status: 'active', buy_probability: 35, sell_probability: 25, hold_probability: 40 },
];

const timeframes = ['5M', '15M', '1H', '4H', '1D'] as const;

function formatPrice(price: number) {
  return price < 1
    ? `$${price.toFixed(4)}`
    : `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function Metric({
  label,
  value,
  change,
  icon: Icon,
}: {
  label: string;
  value: string;
  change: string;
  icon: typeof Wallet;
}) {
  return (
    <div className="rounded-xl border border-white/[0.07] bg-[#0a1014]/90 p-4 transition hover:border-white/[0.12] sm:p-5">
      <div className="flex items-center justify-between">
        <p className="text-[10px] font-semibold uppercase tracking-[0.13em] text-surface-500">{label}</p>
        <Icon className="h-4 w-4 text-surface-500" />
      </div>
      <p className="mt-3 font-mono text-xl font-semibold tracking-tight text-white sm:text-2xl">{value}</p>
      <p className="mt-1.5 text-[11px] text-primary-400">{change}</p>
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuthStore();
  const { tradingMode, killSwitchActive, isConnected } = useTradingStore();
  const [loading, setLoading] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [timeframe, setTimeframe] = useState<(typeof timeframes)[number]>('1H');

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 500);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="space-y-5">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => <CardSkeleton key={index} />)}
        </div>
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
          <div className="xl:col-span-2"><CardSkeleton /></div>
          <CardSkeleton />
        </div>
      </div>
    );
  }

  const selectedMarket = demoMarkets.find((market) => market.symbol === selectedSymbol) ?? demoMarkets[0];
  const selectedSignal = demoSignals.find((signal) => signal.symbol === selectedSymbol);

  return (
    <div className="mx-auto max-w-[1600px] space-y-5 pb-8">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-semibold tracking-tight text-white sm:text-2xl">Good to see you, {user?.full_name?.split(' ')[0] || 'Trader'}</h1>
            <Sparkles className="hidden h-4 w-4 text-primary-400 sm:block" />
          </div>
          <p className="mt-1 text-xs text-surface-500">Here’s your market overview for today.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <div className="inline-flex items-center gap-2 rounded-lg border border-primary-400/15 bg-primary-400/[0.05] px-3 py-2">
            <span className="relative flex h-2 w-2">
              <span className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-60 ${isConnected ? 'bg-primary-400' : 'bg-amber-400'}`} />
              <span className={`relative inline-flex h-2 w-2 rounded-full ${isConnected ? 'bg-primary-400' : 'bg-amber-400'}`} />
            </span>
            <span className="text-[10px] font-medium text-surface-300">{isConnected ? 'Exchange connected' : 'Demo environment'}</span>
          </div>
          <span className="inline-flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-white/[0.025] px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-surface-300">
            <ShieldCheck className="h-3.5 w-3.5 text-primary-400" /> {tradingMode} mode
          </span>
          <Link to="/trading" className="inline-flex items-center gap-2 rounded-lg bg-primary-500 px-3.5 py-2 text-xs font-semibold text-surface-950 transition hover:bg-primary-400">
            Open terminal <ExternalLink className="h-3.5 w-3.5" />
          </Link>
        </div>
      </div>

      <div className="flex items-start gap-2.5 rounded-lg border border-amber-400/15 bg-amber-400/[0.035] px-3.5 py-2.5">
        <Zap className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-300" />
        <p className="text-[11px] leading-5 text-amber-200/80"><span className="font-semibold text-amber-200">SIMULATED DATA</span> · Market prices and portfolio figures are for demonstration only. No real funds are being traded.</p>
      </div>

      {killSwitchActive && (
        <div className="flex items-center gap-2 rounded-lg border border-rose-400/20 bg-rose-400/[0.06] px-4 py-3 text-xs font-medium text-rose-300">
          <Activity className="h-4 w-4" /> Kill switch is active. Trading actions are disabled.
        </div>
      )}

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Metric label="Portfolio balance" value="$10,247.83" change="+$247.83 · +2.48% overall" icon={BriefcaseBusiness} />
        <Metric label="Today's P&L" value="+$87.50" change="+0.87% today" icon={CircleDollarSign} />
        <Metric label="Win rate" value="62.5%" change="+3.2% vs. last week" icon={BarChart3} />
        <Metric label="Available balance" value="$8,247.83" change="80.5% of portfolio" icon={Wallet} />
      </div>

      <div className="grid min-w-0 grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_310px]">
        <section className="min-w-0 overflow-hidden rounded-xl border border-white/[0.07] bg-[#090f13]">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.07] px-4 py-3 sm:px-5">
            <div className="flex flex-wrap items-center gap-3">
              <label className="relative">
                <span className="sr-only">Choose market</span>
                <select
                  value={selectedSymbol}
                  onChange={(event) => setSelectedSymbol(event.target.value)}
                  className="appearance-none rounded-md border border-white/[0.09] bg-white/[0.035] py-2 pl-3 pr-8 text-xs font-semibold text-white outline-none transition focus:border-primary-400/40"
                >
                  {demoMarkets.map((market) => <option key={market.symbol} value={market.symbol} className="bg-surface-900">{market.symbol}</option>)}
                </select>
                <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-surface-500" />
              </label>
              <div>
                <p className="font-mono text-sm font-semibold text-white">{formatPrice(selectedMarket.price)}</p>
                <p className={`mt-0.5 text-[10px] ${selectedMarket.change_24h >= 0 ? 'text-primary-400' : 'text-rose-400'}`}>
                  {selectedMarket.change_24h >= 0 ? '+' : ''}{selectedMarket.change_24h.toFixed(2)}% <span className="text-surface-600">24h</span>
                </p>
              </div>
            </div>
            <Link to="/trading" className="hidden items-center gap-1.5 text-[10px] font-medium text-surface-400 transition hover:text-primary-300 sm:inline-flex">
              Full chart <ExternalLink className="h-3 w-3" />
            </Link>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/[0.06] px-4 py-2.5 sm:px-5">
            <div className="flex items-center gap-1">
              {timeframes.map((frame) => (
                <button
                  key={frame}
                  type="button"
                  onClick={() => setTimeframe(frame)}
                  aria-pressed={timeframe === frame}
                  className={`rounded px-2.5 py-1 text-[10px] font-medium transition ${timeframe === frame ? 'bg-primary-400/10 text-primary-300' : 'text-surface-500 hover:bg-white/[0.04] hover:text-surface-300'}`}
                >
                  {frame}
                </button>
              ))}
            </div>
            <span className="inline-flex items-center gap-1.5 text-[9px] text-surface-500"><span className="h-1.5 w-1.5 rounded-full bg-primary-400" /> BINANCE · SPOT</span>
          </div>

          <div className="min-w-0 p-2 sm:p-3">
            <CandlestickChart key={`${selectedSymbol}-${timeframe}`} symbol={selectedSymbol} timeframe={timeframe} height={315} />
          </div>

          <div className="grid grid-cols-2 gap-px border-t border-white/[0.06] bg-white/[0.06] sm:grid-cols-4">
            {[
              { label: '24H HIGH', value: formatPrice(selectedMarket.high_24h) },
              { label: '24H LOW', value: formatPrice(selectedMarket.low_24h) },
              { label: '24H VOLUME', value: `$${(selectedMarket.volume_24h / 1e9).toFixed(1)}B` },
              { label: 'LIQUIDITY', value: `${selectedMarket.liquidity_score}/100` },
            ].map((item) => (
              <div key={item.label} className="bg-[#090f13] px-4 py-3">
                <p className="text-[9px] font-medium tracking-wider text-surface-600">{item.label}</p>
                <p className="mt-1 font-mono text-xs font-medium text-surface-200">{item.value}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="overflow-hidden rounded-xl border border-white/[0.07] bg-[#090f13]">
          <div className="flex items-center justify-between border-b border-white/[0.07] px-4 py-3.5">
            <div>
              <h2 className="text-xs font-semibold text-white">Market watchlist</h2>
              <p className="mt-1 text-[10px] text-surface-600">Top markets · 24 hour</p>
            </div>
            <Link to="/scanner" aria-label="Open market scanner" className="rounded-md p-1.5 text-surface-500 transition hover:bg-white/[0.05] hover:text-primary-300"><Layers3 className="h-4 w-4" /></Link>
          </div>
          <div className="divide-y divide-white/[0.045]">
            {demoMarkets.map((market) => {
              const signal = demoSignals.find((item) => item.symbol === market.symbol);
              const selected = market.symbol === selectedSymbol;
              return (
                <button
                  key={market.symbol}
                  type="button"
                  onClick={() => setSelectedSymbol(market.symbol)}
                  aria-pressed={selected}
                  className={`flex w-full items-center justify-between gap-2 px-4 py-3.5 text-left transition ${selected ? 'bg-primary-400/[0.055]' : 'hover:bg-white/[0.025]'}`}
                >
                  <span className="flex min-w-0 items-center gap-2.5">
                    <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border text-[10px] font-bold ${selected ? 'border-primary-400/20 bg-primary-400/10 text-primary-300' : 'border-white/[0.07] bg-white/[0.03] text-surface-300'}`}>{market.base.slice(0, 1)}</span>
                    <span className="min-w-0">
                      <span className="block text-xs font-semibold text-surface-200">{market.base}<span className="ml-1 text-[9px] font-normal text-surface-600">/ USDT</span></span>
                      <span className="mt-1 block text-[9px] text-surface-600">{signal ? `${signal.signal} · ${signal.confidence}% confidence` : 'Market overview'}</span>
                    </span>
                  </span>
                  <span className="shrink-0 text-right">
                    <span className="block font-mono text-[10px] text-surface-200">{formatPrice(market.price)}</span>
                    <span className={`mt-1 inline-flex items-center justify-end text-[10px] ${market.change_24h >= 0 ? 'text-primary-400' : 'text-rose-400'}`}>
                      {market.change_24h >= 0 ? <ArrowUpRight className="mr-0.5 h-3 w-3" /> : <ArrowDownRight className="mr-0.5 h-3 w-3" />}
                      {Math.abs(market.change_24h).toFixed(2)}%
                    </span>
                  </span>
                </button>
              );
            })}
          </div>
          <Link to="/scanner" className="flex items-center justify-center gap-1.5 border-t border-white/[0.06] py-3 text-[10px] font-medium text-surface-500 transition hover:text-primary-300">
            View market scanner <ExternalLink className="h-3 w-3" />
          </Link>
        </section>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1fr_1fr_0.9fr]">
        <section className="rounded-xl border border-white/[0.07] bg-[#090f13] p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xs font-semibold text-white">AI market insight</h2>
              <p className="mt-1 text-[10px] text-surface-600">{selectedSignal?.strategy ?? 'Market analysis'} · {selectedSignal?.timeframe ?? '24H'} context</p>
            </div>
            <span className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-400/15 bg-cyan-400/[0.06] text-cyan-300"><BrainCircuit className="h-4 w-4" /></span>
          </div>
          {selectedSignal ? (
            <>
              <div className="mt-4 flex items-center gap-2">
                <StatusBadge status={selectedSignal.signal} size="sm" />
                <span className="text-[10px] text-surface-500">{selectedSignal.symbol}</span>
                <span className="ml-auto font-mono text-xs font-semibold text-primary-300">{selectedSignal.confidence}% <span className="font-sans font-normal text-surface-600">confidence</span></span>
              </div>
              <p className="mt-3 text-[11px] leading-5 text-surface-400">{selectedSignal.reasoning_summary}</p>
              <div className="mt-4 grid grid-cols-3 gap-2 border-t border-white/[0.06] pt-3">
                <div><p className="text-[9px] text-surface-600">ENTRY</p><p className="mt-1 font-mono text-[10px] text-surface-200">{formatPrice(selectedSignal.entry_price)}</p></div>
                <div><p className="text-[9px] text-surface-600">STOP LOSS</p><p className="mt-1 font-mono text-[10px] text-rose-300">{formatPrice(selectedSignal.stop_loss)}</p></div>
                <div><p className="text-[9px] text-surface-600">RISK / REWARD</p><p className="mt-1 font-mono text-[10px] text-surface-200">1:{selectedSignal.risk_reward}</p></div>
              </div>
            </>
          ) : (
            <div className="mt-4 rounded-lg border border-white/[0.06] bg-white/[0.02] p-3">
              <p className="text-[11px] leading-5 text-surface-400">No active demo signal for {selectedSymbol}. Review the chart and your own strategy before making a decision.</p>
            </div>
          )}
          <Link to="/signals" className="mt-4 inline-flex items-center gap-1.5 text-[10px] font-medium text-primary-300 transition hover:text-primary-200">Explore AI signals <ExternalLink className="h-3 w-3" /></Link>
        </section>

        <section className="rounded-xl border border-white/[0.07] bg-[#090f13] p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xs font-semibold text-white">Risk overview</h2>
              <p className="mt-1 text-[10px] text-surface-600">Portfolio guardrails</p>
            </div>
            <Gauge className="h-4 w-4 text-primary-400" />
          </div>
          <div className="mt-5 space-y-4">
            {[
              { label: 'Daily loss limit', value: '0.9% of 2.0%', fill: '45%', color: 'bg-primary-400' },
              { label: 'Current drawdown', value: '1.2% of 5.0%', fill: '24%', color: 'bg-cyan-400' },
              { label: 'Portfolio exposure', value: '19.5%', fill: '39%', color: 'bg-primary-400' },
            ].map((item) => (
              <div key={item.label}>
                <div className="flex items-center justify-between gap-2 text-[10px]">
                  <span className="text-surface-400">{item.label}</span><span className="font-mono text-surface-300">{item.value}</span>
                </div>
                <div className="mt-2 h-1 overflow-hidden rounded-full bg-white/[0.07]"><div className={`h-full rounded-full ${item.color}`} style={{ width: item.fill }} /></div>
              </div>
            ))}
          </div>
          <div className="mt-4 flex items-center justify-between border-t border-white/[0.06] pt-3">
            <span className="inline-flex items-center gap-1.5 text-[10px] text-primary-300"><ShieldCheck className="h-3.5 w-3.5" /> {killSwitchActive ? 'Trading paused' : 'Within demo limits'}</span>
            <Link to="/risk" className="text-[10px] font-medium text-surface-500 transition hover:text-primary-300">Settings <ExternalLink className="ml-0.5 inline h-3 w-3" /></Link>
          </div>
        </section>

        <section className="rounded-xl border border-white/[0.07] bg-[#090f13] p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xs font-semibold text-white">Recent activity</h2>
              <p className="mt-1 text-[10px] text-surface-600">Demo workspace</p>
            </div>
            <Clock3 className="h-4 w-4 text-surface-500" />
          </div>
          <div className="mt-4 space-y-4">
            {[
              { title: 'Market analysis completed', detail: 'BTC/USDT · Trend following', time: '2 min ago', icon: BrainCircuit, color: 'text-cyan-300 bg-cyan-400/[0.08]' },
              { title: 'Watchlist updated', detail: '5 markets tracked', time: '18 min ago', icon: Activity, color: 'text-primary-300 bg-primary-400/[0.08]' },
              { title: 'Risk limits reviewed', detail: 'Paper portfolio · All clear', time: '1 hr ago', icon: ShieldCheck, color: 'text-amber-300 bg-amber-400/[0.08]' },
            ].map((item) => (
              <div key={item.title} className="flex items-center gap-2.5">
                <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${item.color}`}><item.icon className="h-3.5 w-3.5" /></span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-[10px] font-medium text-surface-200">{item.title}</p>
                  <p className="mt-1 truncate text-[9px] text-surface-600">{item.detail}</p>
                </div>
                <span className="shrink-0 text-[9px] text-surface-600">{item.time}</span>
              </div>
            ))}
          </div>
          <Link to="/journal" className="mt-4 inline-flex items-center gap-1.5 border-t border-white/[0.06] pt-3 text-[10px] font-medium text-surface-500 transition hover:text-primary-300">Open trade journal <ExternalLink className="h-3 w-3" /></Link>
        </section>
      </div>
    </div>
  );
}
