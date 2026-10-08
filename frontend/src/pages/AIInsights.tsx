import { motion } from 'framer-motion'
import { Brain, Sparkles, TrendingUp, AlertTriangle, Zap, Target, Shield, BarChart3 } from 'lucide-react'

const insights = [
  {
    type: 'opportunity',
    icon: TrendingUp,
    title: 'BTC Breakout Pattern Detected',
    description: 'BTC/USDT showing strong bullish divergence on 4H chart. Historical accuracy: 78%.',
    confidence: 85,
    timeframe: '4H',
    asset: 'BTC/USDT',
  },
  {
    type: 'risk',
    icon: AlertTriangle,
    title: 'High Volatility Warning',
    description: 'ETH volatility index spiked 45%. Consider reducing position size.',
    confidence: 92,
    timeframe: '1H',
    asset: 'ETH/USDT',
  },
  {
    type: 'signal',
    icon: Zap,
    title: 'SOL Momentum Signal',
    description: 'Strong buying pressure detected. Volume profile suggests accumulation phase.',
    confidence: 76,
    timeframe: '1D',
    asset: 'SOL/USDT',
  },
  {
    type: 'analysis',
    icon: BarChart3,
    title: 'Market Sentiment Shift',
    description: 'Fear & Greed index moved from Neutral to Greed. Historical correction probability: 34%.',
    confidence: 68,
    timeframe: '1W',
    asset: 'Market',
  },
]

const aiModels = [
  { name: 'Trend Predictor', accuracy: 78.4, status: 'active', version: 'v2.4.1' },
  { name: 'Sentiment Analyzer', accuracy: 82.1, status: 'active', version: 'v3.1.0' },
  { name: 'Risk Assessor', accuracy: 91.7, status: 'active', version: 'v1.8.3' },
  { name: 'Volume Profile', accuracy: 74.2, status: 'training', version: 'v2.0.0-beta' },
]

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
}

export default function AIInsights() {
  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-8"
    >
      {/* Page Header */}
      <motion.div variants={item} className="page-header">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-accent-500 to-primary-500 flex items-center justify-center">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="page-title">AI Insights</h1>
            <p className="page-subtitle">Machine learning-powered trading intelligence</p>
          </div>
        </div>
      </motion.div>

      {/* AI Status Banner */}
      <motion.div variants={item} className="glass-card p-6 border-accent-500/20">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-3 h-3 rounded-full bg-primary-500 pulse-dot" />
            <div>
              <h3 className="font-semibold text-surface-100">AI Engine Active</h3>
              <p className="text-sm text-surface-400">Processing 1,247 signals across 50+ markets</p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-right">
              <p className="text-sm text-surface-400">Signals Today</p>
              <p className="text-xl font-bold font-number text-accent-400">47</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-surface-400">Accuracy</p>
              <p className="text-xl font-bold font-number text-primary-400">81.2%</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Insights Grid */}
      <motion.div variants={item}>
        <h2 className="text-lg font-semibold text-surface-100 mb-4 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-accent-400" />
          Latest Insights
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {insights.map((insight, i) => (
            <motion.div
              key={i}
              variants={item}
              className="glass-card-hover p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                  insight.type === 'opportunity' ? 'bg-primary-500/10 text-primary-400' :
                  insight.type === 'risk' ? 'bg-danger-500/10 text-danger-400' :
                  insight.type === 'signal' ? 'bg-accent-500/10 text-accent-400' :
                  'bg-surface-700/50 text-surface-300'
                }`}>
                  <insight.icon className="w-5 h-5" />
                </div>
                <span className="badge-neutral">{insight.asset}</span>
              </div>
              <h3 className="font-semibold text-surface-100 mb-2">{insight.title}</h3>
              <p className="text-sm text-surface-400 mb-4">{insight.description}</p>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-surface-500" />
                  <span className="text-xs text-surface-500">{insight.timeframe}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-surface-500">Confidence</span>
                  <div className="progress-bar w-20">
                    <div
                      className={`progress-fill ${insight.confidence >= 80 ? 'bg-primary-500' : insight.confidence >= 60 ? 'bg-accent-500' : 'bg-surface-500'}`}
                      style={{ width: `${insight.confidence}%` }}
                    />
                  </div>
                  <span className="text-xs font-number text-surface-300">{insight.confidence}%</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* AI Models */}
      <motion.div variants={item} className="glass-card">
        <div className="card-header">
          <h2 className="text-lg font-semibold text-surface-100 flex items-center gap-2">
            <Shield className="w-5 h-5 text-primary-400" />
            AI Models
          </h2>
        </div>
        <div className="table-container">
          <table className="w-full">
            <thead>
              <tr className="table-header">
                <th className="text-left px-6 py-3">Model</th>
                <th className="text-left px-6 py-3">Version</th>
                <th className="text-right px-6 py-3">Accuracy</th>
                <th className="text-right px-6 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {aiModels.map((model) => (
                <tr key={model.name} className="table-row">
                  <td className="table-cell font-medium text-surface-200">{model.name}</td>
                  <td className="table-cell text-surface-400 font-mono text-sm">{model.version}</td>
                  <td className="table-cell text-right">
                    <span className="font-number text-primary-400">{model.accuracy}%</span>
                  </td>
                  <td className="table-cell text-right">
                    <span className={model.status === 'active' ? 'badge-buy' : 'badge-neutral'}>
                      {model.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </motion.div>
  )
}
