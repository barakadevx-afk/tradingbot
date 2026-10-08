import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Brain,
  Shield,
  BarChart3,
  TrendingUp,
  Zap,
  Lock,
  ArrowRight,
  CheckCircle,
  Activity,
  Target,
  LineChart,
} from 'lucide-react';

const pipeline = [
  { title: 'Live Market Data', desc: 'Real-time OHLCV, order book, and trade flow', icon: Activity },
  { title: 'Technical Analysis', desc: 'Multi-timeframe indicators and market structure', icon: LineChart },
  { title: 'AI Intelligence', desc: 'ML-powered predictions with confidence scoring', icon: Brain },
  { title: 'Signal Generation', desc: 'BUY / SELL / HOLD with risk/reward analysis', icon: Target },
  { title: 'Risk Management', desc: 'Capital protection with position sizing', icon: Shield },
  { title: 'Trade Execution', desc: 'Paper trading with realistic simulation', icon: Zap },
  { title: 'Position Monitoring', desc: 'Real-time P&L and exit management', icon: TrendingUp },
  { title: 'Performance Analytics', desc: 'Comprehensive trade journal and metrics', icon: BarChart3 },
];

const features = [
  {
    icon: Brain,
    title: 'AI-Powered Analysis',
    desc: 'Machine learning models analyze multiple timeframes to generate high-confidence trading signals with full transparency.',
  },
  {
    icon: Shield,
    title: 'Risk-First Architecture',
    desc: 'Every signal passes through a mandatory risk engine. No risk approval, no trade. Capital protection is paramount.',
  },
  {
    icon: BarChart3,
    title: 'Professional Backtesting',
    desc: 'Test strategies with realistic fees, slippage, and walk-forward validation before risking any capital.',
  },
  {
    icon: Lock,
    title: 'Security by Design',
    desc: 'Encrypted credentials, JWT authentication, role-based access, and comprehensive audit logging.',
  },
  {
    icon: Activity,
    title: 'Real-Time Monitoring',
    desc: 'Live system health monitoring, data quality checks, and automatic kill switch protection.',
  },
  {
    icon: Target,
    title: 'Multi-Strategy Engine',
    desc: 'Trend following, breakout, pullback, and mean reversion strategies with regime adaptation.',
  },
];

const stats = [
  { value: '7+', label: 'Supported Markets' },
  { value: '5', label: 'Timeframes' },
  { value: '20+', label: 'Technical Indicators' },
  { value: '100%', label: 'Paper Trading' },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Navigation */}
      <nav className="fixed top-0 z-50 w-full border-b border-slate-800/50 bg-slate-950/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-cyan-500">
              <Brain className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight">BARAKA AI</span>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-slate-400 hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="text-sm text-slate-400 hover:text-white transition-colors">How It Works</a>
            <a href="#security" className="text-sm text-slate-400 hover:text-white transition-colors">Security</a>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-400 transition-colors"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative pt-32 pb-20 px-4 lg:px-8 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/5 via-transparent to-transparent" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full bg-emerald-500/5 blur-3xl" />
        
        <div className="relative mx-auto max-w-7xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1.5 text-sm text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              Intelligent Crypto Trading Platform
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
              <span className="bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                BARAKA AI
              </span>
            </h1>
            <p className="mt-4 text-2xl md:text-3xl font-semibold text-emerald-400">
              Trade Smarter. Grow Faster.
            </p>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
              Advanced crypto market intelligence, AI-powered signals, quantitative strategies
              and professional risk management in one platform.
            </p>
            
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                to="/register"
                className="group flex items-center gap-2 rounded-xl bg-emerald-500 px-8 py-4 text-lg font-semibold text-white hover:bg-emerald-400 transition-all shadow-lg shadow-emerald-500/20"
              >
                Launch Dashboard
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/login"
                className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/50 px-8 py-4 text-lg font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition-all"
              >
                Explore Demo
              </Link>
            </div>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8"
          >
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <p className="text-3xl font-bold text-white">{stat.value}</p>
                <p className="mt-1 text-sm text-slate-500">{stat.label}</p>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-4 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold">Professional-Grade Features</h2>
            <p className="mt-4 text-slate-400 max-w-2xl mx-auto">
              Everything you need for intelligent crypto trading, from market analysis to execution.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                className="rounded-xl border border-slate-800/50 bg-slate-900/50 p-6 hover:border-slate-700/50 transition-all"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
                <p className="mt-2 text-sm text-slate-400">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 px-4 lg:px-8 bg-slate-900/30">
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold">How BARAKA AI Works</h2>
            <p className="mt-4 text-slate-400 max-w-2xl mx-auto">
              A systematic pipeline from market data to performance analytics.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {pipeline.map((step, i) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                className="relative"
              >
                <div className="rounded-xl border border-slate-800/50 bg-slate-900/50 p-5 h-full">
                  <div className="mb-3 flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-400 text-sm font-bold">
                      {i + 1}
                    </div>
                    <step.icon className="h-5 w-5 text-slate-500" />
                  </div>
                  <h3 className="font-semibold text-white">{step.title}</h3>
                  <p className="mt-1 text-xs text-slate-500">{step.desc}</p>
                </div>
                {i < pipeline.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-2 transform -translate-y-1/2">
                    <ArrowRight className="h-4 w-4 text-slate-700" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Security */}
      <section id="security" className="py-20 px-4 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="rounded-2xl border border-slate-800/50 bg-slate-900/50 p-8 md:p-12">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <h2 className="text-3xl font-bold">Security First</h2>
                <p className="mt-4 text-slate-400">
                  BARAKA AI is built with security as a foundational principle, not an afterthought.
                </p>
                <ul className="mt-6 space-y-3">
                  {[
                    'Encrypted exchange API credentials',
                    'JWT authentication with refresh tokens',
                    'Role-based access control (RBAC)',
                    'Comprehensive audit logging',
                    'Rate limiting and input validation',
                    'No withdrawal permissions required',
                  ].map((item) => (
                    <li key={item} className="flex items-center gap-3 text-sm text-slate-300">
                      <CheckCircle className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="flex items-center justify-center">
                <div className="relative">
                  <div className="h-48 w-48 rounded-full bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 flex items-center justify-center">
                    <div className="h-32 w-32 rounded-full bg-gradient-to-br from-emerald-500/30 to-cyan-500/30 flex items-center justify-center">
                      <Lock className="h-16 w-16 text-emerald-400" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="text-3xl md:text-4xl font-bold">Ready to Trade Smarter?</h2>
          <p className="mt-4 text-slate-400">
            Start with paper trading. No real money required. Test strategies, learn the platform, and grow your skills.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="rounded-xl bg-emerald-500 px-8 py-4 text-lg font-semibold text-white hover:bg-emerald-400 transition-all shadow-lg shadow-emerald-500/20"
            >
              Start Paper Trading
            </Link>
            <Link
              to="/login"
              className="rounded-xl border border-slate-700 px-8 py-4 text-lg font-semibold text-slate-300 hover:bg-slate-800 transition-all"
            >
              Sign In
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-12 px-4 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-cyan-500">
                <Brain className="h-4 w-4 text-white" />
              </div>
              <span className="font-bold">BARAKA AI</span>
            </div>
            <p className="text-sm text-slate-500">
              Trade Smarter. Grow Faster. | Intelligent Crypto Trading Platform
            </p>
            <p className="text-xs text-slate-600">
              BARAKA AI does not guarantee profit. Trading involves risk.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
