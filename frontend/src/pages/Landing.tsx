import {
  Activity,
  ArrowRight,
  BarChart3,
  BrainCircuit,
  Check,
  ChevronRight,
  CircleDollarSign,
  Clock3,
  Crosshair,
  Database,
  Gauge,
  LockKeyhole,
  Radar,
  ShieldCheck,
  Sparkles,
  Waypoints,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import CandlestickChart from '../components/CandlestickChart';

const features = [
  {
    icon: Radar,
    title: 'Market intelligence',
    description: 'Scan markets, compare momentum, and read multi-timeframe conditions from one focused workspace.',
    tag: '01 / ANALYZE',
  },
  {
    icon: BrainCircuit,
    title: 'AI-assisted signals',
    description: 'Explore strategy signals with confidence scores, clear reasoning, and the context behind each idea.',
    tag: '02 / INTERPRET',
  },
  {
    icon: ShieldCheck,
    title: 'Risk by design',
    description: 'Set position sizing, stop losses, and drawdown guardrails before you put a strategy to work.',
    tag: '03 / PROTECT',
  },
  {
    icon: BarChart3,
    title: 'Strategy backtesting',
    description: 'Review how a strategy behaved against historical data before testing it in a simulated environment.',
    tag: '04 / VALIDATE',
  },
  {
    icon: Waypoints,
    title: 'One connected workflow',
    description: 'Move naturally from market analysis to orders, portfolio monitoring, and a searchable trade journal.',
    tag: '05 / ORGANIZE',
  },
  {
    icon: Database,
    title: 'A complete audit trail',
    description: 'Keep your signals, decisions, and trade outcomes together so every result is easier to review.',
    tag: '06 / REVIEW',
  },
];

const steps = [
  { number: '01', title: 'Explore the market', description: 'Review live market context, charts, and technical indicators.' },
  { number: '02', title: 'Build a strategy', description: 'Choose your approach and configure the indicators that matter to you.' },
  { number: '03', title: 'Set your risk', description: 'Define position sizes, stop losses, and account-level limits.' },
  { number: '04', title: 'Test and review', description: 'Paper trade your plan, then learn from clear performance analytics.' },
];

const marketRows = [
  { symbol: 'BTC', name: 'Bitcoin', price: '$67,432.50', change: '+2.34%', positive: true },
  { symbol: 'ETH', name: 'Ethereum', price: '$3,542.80', change: '+1.87%', positive: true },
  { symbol: 'SOL', name: 'Solana', price: '$178.45', change: '-0.92%', positive: false },
];

export default function Landing() {
  return (
    <div className="landing-page min-h-screen overflow-hidden bg-surface-950 text-surface-100">
      <header className="fixed inset-x-0 top-0 z-50 border-b border-white/[0.07] bg-surface-950/85 backdrop-blur-xl">
        <nav aria-label="Main navigation" className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-5 lg:px-8">
          <Link to="/" className="flex items-center gap-3" aria-label="BARAKA home">
            <img src="/logo.svg" alt="" className="h-9 w-9" />
            <span className="text-sm font-bold tracking-[0.12em] text-white">BARAKA<span className="ml-1.5 text-[9px] font-medium tracking-[0.2em] text-surface-400">TRADING BOT</span></span>
          </Link>

          <div className="hidden items-center gap-8 md:flex">
            <a href="#features" className="text-sm text-surface-400 transition hover:text-white">Features</a>
            <a href="#how-it-works" className="text-sm text-surface-400 transition hover:text-white">How it works</a>
            <a href="#risk" className="text-sm text-surface-400 transition hover:text-white">Risk management</a>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            <Link to="/login" className="rounded-lg px-3 py-2 text-sm font-medium text-surface-300 transition hover:text-white">Sign in</Link>
            <Link to="/register" className="inline-flex items-center gap-2 rounded-lg bg-primary-500 px-4 py-2.5 text-sm font-semibold text-surface-950 shadow-[0_0_24px_rgba(34,197,94,0.18)] transition hover:bg-primary-400">
              Get started <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </nav>
      </header>

      <main>
        <section className="relative px-5 pb-20 pt-32 sm:pt-36 lg:px-8 lg:pb-28 lg:pt-40">
          <div className="pointer-events-none absolute -left-48 top-12 h-[32rem] w-[32rem] rounded-full bg-primary-500/[0.08] blur-[120px]" />
          <div className="pointer-events-none absolute right-[-12rem] top-24 h-[36rem] w-[36rem] rounded-full bg-cyan-500/[0.06] blur-[140px]" />
          <div className="relative mx-auto grid max-w-7xl items-center gap-14 lg:grid-cols-[0.9fr_1.1fr] lg:gap-12">
            <div className="relative z-10">
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-primary-400/20 bg-primary-400/[0.08] px-3.5 py-1.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-primary-300">
                <Sparkles className="h-3.5 w-3.5" />
                A smarter trading workspace
              </div>
              <h1 className="max-w-2xl text-[2.8rem] font-semibold leading-[1.06] tracking-[-0.055em] text-white sm:text-6xl lg:text-[4.25rem]">
                Smarter analysis.
                <span className="mt-1 block bg-gradient-to-r from-primary-300 via-primary-400 to-cyan-300 bg-clip-text text-transparent">Better decisions.</span>
              </h1>
              <p className="mt-6 max-w-xl text-base leading-7 text-surface-400 sm:text-lg sm:leading-8">
                Bring market analysis, AI-assisted signals, and disciplined risk controls into one clear trading workflow. Explore every strategy in paper mode before you decide what comes next.
              </p>

              <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                <Link to="/register" className="group inline-flex items-center justify-center gap-2 rounded-lg bg-primary-500 px-5 py-3 text-sm font-bold text-surface-950 transition hover:bg-primary-400">
                  Start paper trading
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
                <a href="#how-it-works" className="inline-flex items-center justify-center gap-2 rounded-lg border border-white/10 bg-white/[0.03] px-5 py-3 text-sm font-semibold text-surface-200 transition hover:border-white/20 hover:bg-white/[0.06]">
                  See how it works <ChevronRight className="h-4 w-4 text-surface-400" />
                </a>
              </div>

              <div className="mt-9 flex flex-wrap items-center gap-x-6 gap-y-3 text-xs text-surface-400">
                <span className="inline-flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full bg-primary-400 shadow-[0_0_10px_rgba(74,222,128,0.8)]" />Paper trading by default</span>
                <span className="inline-flex items-center gap-2"><LockKeyhole className="h-3.5 w-3.5 text-surface-500" />Your risk, your rules</span>
              </div>
            </div>

            <div className="relative mx-auto w-full max-w-2xl">
              <div className="pointer-events-none absolute -inset-5 rounded-[2rem] bg-gradient-to-br from-primary-400/10 via-transparent to-cyan-400/[0.07] blur-2xl" />
              <div className="relative overflow-hidden rounded-2xl border border-white/[0.11] bg-[#080e12] shadow-[0_28px_100px_rgba(0,0,0,0.55)]">
                <div className="flex items-center justify-between border-b border-white/[0.07] px-4 py-3 sm:px-5">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1.5" aria-hidden="true">
                      <span className="h-2 w-2 rounded-full bg-[#ff6058]" /><span className="h-2 w-2 rounded-full bg-[#ffbd2e]" /><span className="h-2 w-2 rounded-full bg-[#28c840]" />
                    </div>
                    <span className="hidden text-[11px] text-surface-500 sm:block">BARAKA / MARKET TERMINAL</span>
                  </div>
                  <span className="inline-flex items-center gap-1.5 rounded-md border border-primary-400/15 bg-primary-400/[0.07] px-2 py-1 text-[9px] font-semibold uppercase tracking-wider text-primary-300">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary-400" /> Paper mode
                  </span>
                </div>

                <div className="grid grid-cols-3 divide-x divide-white/[0.06] border-b border-white/[0.07]">
                  {[
                    { label: 'BTC / USDT', value: '$67,432.50', change: '+2.34%', positive: true },
                    { label: 'PORTFOLIO', value: '$10,247.83', change: '+2.48%', positive: true },
                    { label: 'OPEN RISK', value: '1.2%', change: 'Within limits', positive: false },
                  ].map((metric) => (
                    <div key={metric.label} className="min-w-0 px-3 py-3.5 sm:px-4">
                      <p className="truncate text-[9px] font-medium tracking-[0.12em] text-surface-500 sm:text-[10px]">{metric.label}</p>
                      <p className="mt-1 truncate font-mono text-xs font-semibold text-surface-100 sm:text-sm">{metric.value}</p>
                      <p className={`mt-1 truncate text-[10px] ${metric.change === 'Within limits' ? 'text-primary-300' : metric.positive ? 'text-primary-400' : 'text-rose-400'}`}>{metric.change}</p>
                    </div>
                  ))}
                </div>

                <div className="grid min-w-0 lg:grid-cols-[1fr_190px]">
                  <div className="min-w-0 border-b border-white/[0.07] p-2 sm:p-3 lg:border-b-0 lg:border-r">
                    <div className="flex items-center justify-between px-2 pb-2 pt-1">
                      <div>
                        <p className="text-xs font-semibold text-white">Bitcoin / Tether</p>
                        <p className="mt-0.5 text-[10px] text-surface-500">BINANCE · 1H</p>
                      </div>
                      <span className="font-mono text-[10px] text-primary-300">+2.34%</span>
                    </div>
                    <CandlestickChart symbol="BTC/USDT" timeframe="1H" height={285} />
                  </div>

                  <aside className="hidden p-4 lg:block">
                    <div className="flex items-center justify-between">
                      <p className="text-[10px] font-semibold uppercase tracking-[0.13em] text-surface-400">Watchlist</p>
                      <Activity className="h-3.5 w-3.5 text-primary-400" />
                    </div>
                    <div className="mt-3 space-y-1">
                      {marketRows.map((market) => (
                        <div key={market.symbol} className="rounded-lg px-2 py-2.5 transition hover:bg-white/[0.04]">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold text-surface-200">{market.symbol}</span>
                            <span className={`text-[10px] ${market.positive ? 'text-primary-400' : 'text-rose-400'}`}>{market.change}</span>
                          </div>
                          <div className="mt-1 flex items-center justify-between">
                            <span className="text-[9px] text-surface-500">{market.name}</span>
                            <span className="font-mono text-[9px] text-surface-400">{market.price}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="mt-3 rounded-lg border border-primary-400/15 bg-primary-400/[0.05] p-3">
                      <div className="flex items-center gap-1.5 text-[10px] font-semibold text-primary-300"><BrainCircuit className="h-3.5 w-3.5" /> AI insight</div>
                      <p className="mt-2 text-[10px] leading-4 text-surface-400">BTC momentum is positive. Check your risk settings before acting.</p>
                    </div>
                  </aside>
                </div>
                <div className="flex items-center justify-between border-t border-white/[0.07] bg-black/20 px-4 py-2.5">
                  <span className="text-[9px] text-surface-500">DEMO MARKET DATA · SIMULATED PORTFOLIO</span>
                  <span className="inline-flex items-center gap-1.5 text-[9px] text-primary-300"><span className="h-1.5 w-1.5 rounded-full bg-primary-400" />SYSTEM READY</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="border-y border-white/[0.06] bg-white/[0.015] px-5 py-7 lg:px-8">
          <div className="mx-auto flex max-w-7xl flex-col justify-between gap-5 sm:flex-row sm:items-center">
            <p className="max-w-sm text-sm leading-6 text-surface-400">A complete workspace for thoughtful, data-informed trading.</p>
            <div className="grid grid-cols-2 gap-x-8 gap-y-4 sm:grid-cols-4 sm:gap-8">
              {[
                { icon: Crosshair, label: 'Market analysis' },
                { icon: BrainCircuit, label: 'AI insights' },
                { icon: ShieldCheck, label: 'Risk controls' },
                { icon: CircleDollarSign, label: 'Paper trading' },
              ].map((item) => (
                <div key={item.label} className="flex items-center gap-2.5 text-xs font-medium text-surface-300">
                  <item.icon className="h-4 w-4 text-primary-400" />{item.label}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="features" className="scroll-mt-24 px-5 py-20 sm:py-24 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <div className="mb-10 flex flex-col justify-between gap-5 md:flex-row md:items-end">
              <div className="max-w-2xl">
                <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.2em] text-primary-400">The platform</p>
                <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">Everything in sync.<br className="hidden sm:block" /> Nothing lost in the noise.</h2>
              </div>
              <p className="max-w-md text-sm leading-6 text-surface-400">Practical tools for researching, testing, and reviewing your trading ideas — with the context and controls to make each step your own.</p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {features.map((feature) => (
                <article key={feature.title} className="group rounded-xl border border-white/[0.075] bg-white/[0.025] p-5 transition duration-300 hover:-translate-y-0.5 hover:border-primary-400/25 hover:bg-white/[0.04] sm:p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-primary-400/15 bg-primary-400/[0.08] text-primary-300 transition group-hover:bg-primary-400/[0.13]">
                      <feature.icon className="h-5 w-5" />
                    </div>
                    <span className="font-mono text-[9px] tracking-wider text-surface-600">{feature.tag}</span>
                  </div>
                  <h3 className="mt-5 text-base font-semibold text-white">{feature.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-surface-400">{feature.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="how-it-works" className="scroll-mt-24 border-y border-white/[0.06] bg-[#070b0e] px-5 py-20 sm:py-24 lg:px-8">
          <div className="mx-auto grid max-w-7xl gap-12 lg:grid-cols-[0.75fr_1.25fr] lg:gap-20">
            <div>
              <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.2em] text-primary-400">A calmer process</p>
              <h2 className="text-3xl font-semibold tracking-tight text-white sm:text-4xl">From first look to thoughtful review.</h2>
              <p className="mt-4 max-w-md text-sm leading-6 text-surface-400">The platform keeps your analysis, trading plan, and risk checks connected — so you can focus on the process, not the noise.</p>
              <Link to="/register" className="mt-7 inline-flex items-center gap-2 text-sm font-semibold text-primary-300 transition hover:text-primary-200">
                Explore the workspace <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
            <div className="relative grid gap-3 sm:grid-cols-2">
              {steps.map((step, index) => (
                <article key={step.number} className="relative rounded-xl border border-white/[0.07] bg-white/[0.025] p-5 sm:p-6">
                  <div className="flex items-center justify-between">
                    <span className="flex h-9 w-9 items-center justify-center rounded-full border border-primary-400/25 bg-primary-400/[0.08] font-mono text-xs font-semibold text-primary-300">{step.number}</span>
                    {index === 0 && <Radar className="h-4 w-4 text-surface-600" />}
                    {index === 1 && <BrainCircuit className="h-4 w-4 text-surface-600" />}
                    {index === 2 && <ShieldCheck className="h-4 w-4 text-surface-600" />}
                    {index === 3 && <Clock3 className="h-4 w-4 text-surface-600" />}
                  </div>
                  <h3 className="mt-5 text-sm font-semibold text-white">{step.title}</h3>
                  <p className="mt-2 text-xs leading-5 text-surface-400">{step.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="risk" className="scroll-mt-24 px-5 py-20 sm:py-24 lg:px-8">
          <div className="mx-auto grid max-w-7xl overflow-hidden rounded-2xl border border-white/[0.08] bg-gradient-to-br from-[#0b1513] via-[#080e11] to-[#080b10] lg:grid-cols-[1fr_0.8fr]">
            <div className="p-6 sm:p-9 lg:p-12">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-primary-400/20 bg-primary-400/[0.08] text-primary-300"><ShieldCheck className="h-5 w-5" /></div>
              <p className="mb-3 mt-6 text-[11px] font-semibold uppercase tracking-[0.2em] text-primary-400">Risk management</p>
              <h2 className="max-w-lg text-3xl font-semibold tracking-tight text-white sm:text-4xl">Your strategy. Your limits. Always.</h2>
              <p className="mt-4 max-w-lg text-sm leading-6 text-surface-400">Build risk checks into your routine. Configure stop losses, position sizing, and drawdown limits, then review the plan before you trade.</p>
              <ul className="mt-7 grid gap-3 sm:grid-cols-2">
                {['Position sizing controls', 'Stop-loss planning', 'Drawdown monitoring', 'Paper trading by default'].map((item) => (
                  <li key={item} className="flex items-center gap-2 text-xs text-surface-300"><Check className="h-3.5 w-3.5 text-primary-400" />{item}</li>
                ))}
              </ul>
            </div>
            <div className="border-t border-white/[0.06] bg-black/20 p-6 sm:p-9 lg:border-l lg:border-t-0 lg:p-10">
              <div className="rounded-xl border border-white/[0.08] bg-[#090f12] p-5 shadow-2xl">
                <div className="flex items-center justify-between border-b border-white/[0.07] pb-4">
                  <div>
                    <p className="text-sm font-semibold text-white">Risk overview</p>
                    <p className="mt-1 text-[10px] text-surface-500">Your configured guardrails</p>
                  </div>
                  <Gauge className="h-4 w-4 text-primary-400" />
                </div>
                <div className="mt-5 space-y-4">
                  {[
                    { label: 'Max daily loss', value: '2.0%', fill: 'w-1/3', color: 'bg-primary-400' },
                    { label: 'Portfolio drawdown', value: '1.2%', fill: 'w-1/4', color: 'bg-primary-400' },
                    { label: 'Position exposure', value: '20%', fill: 'w-2/5', color: 'bg-cyan-400' },
                  ].map((setting) => (
                    <div key={setting.label}>
                      <div className="flex justify-between text-[11px]"><span className="text-surface-400">{setting.label}</span><span className="font-mono text-surface-200">{setting.value}</span></div>
                      <div className="mt-2 h-1 overflow-hidden rounded-full bg-white/[0.07]"><div className={`h-full rounded-full ${setting.fill} ${setting.color}`} /></div>
                    </div>
                  ))}
                </div>
                <div className="mt-5 flex items-center gap-2 rounded-lg border border-primary-400/15 bg-primary-400/[0.05] px-3 py-2.5 text-[10px] text-primary-200">
                  <ShieldCheck className="h-3.5 w-3.5 shrink-0 text-primary-400" /> Risk limits configured for paper trading
                </div>
              </div>
            </div>
          </div>
          <p className="mx-auto mt-5 max-w-7xl text-[11px] leading-5 text-surface-500">Trading involves risk and may result in loss. AI-generated signals are probabilistic estimates, not financial advice or guarantees of future results. Paper trading uses simulated funds and does not predict live performance.</p>
        </section>

        <section className="px-5 pb-20 lg:px-8">
          <div className="relative mx-auto max-w-7xl overflow-hidden rounded-2xl border border-primary-400/15 bg-[#08110e] px-6 py-10 text-center sm:px-10 sm:py-14">
            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_50%_120%,rgba(34,197,94,0.13),transparent_60%)]" />
            <div className="relative">
              <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-primary-400">Take the next step</p>
              <h2 className="mx-auto mt-3 max-w-xl text-3xl font-semibold tracking-tight text-white sm:text-4xl">A clearer way to work through the markets.</h2>
              <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-surface-400">Explore the tools, test your ideas with simulated funds, and make every decision your own.</p>
              <Link to="/register" className="mt-6 inline-flex items-center gap-2 rounded-lg bg-primary-500 px-5 py-3 text-sm font-bold text-surface-950 transition hover:bg-primary-400">
                Get started <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-white/[0.07] px-5 py-8 lg:px-8">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <img src="/logo.svg" alt="" className="h-7 w-7" />
            <span className="text-xs font-bold tracking-[0.12em] text-surface-200">BARAKA <span className="font-medium tracking-[0.16em] text-surface-500">TRADING BOT</span></span>
          </Link>
          <div className="flex flex-wrap gap-x-5 gap-y-2 text-xs text-surface-500">
            <a href="#features" className="transition hover:text-surface-200">Features</a>
            <a href="#how-it-works" className="transition hover:text-surface-200">How it works</a>
            <a href="#risk" className="transition hover:text-surface-200">Risk</a>
            <Link to="/login" className="transition hover:text-surface-200">Sign in</Link>
          </div>
          <p className="max-w-md text-[10px] leading-4 text-surface-600">For educational and analytical purposes only. Trading involves substantial risk of loss. Past performance does not guarantee future results.</p>
        </div>
      </footer>
    </div>
  );
}
