import { useState } from 'react';
import { Play, TrendingUp, TrendingDown, Target, BarChart3 } from 'lucide-react';
import { XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import GlassCard from '../components/GlassCard';
import MetricCard from '../components/MetricCard';

const strategies = ['Trend Following', 'Breakout', 'Pullback', 'Mean Reversion', 'SMA Crossover', 'RSI Reversal'];
const symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT'];
const timeframes = ['5M', '15M', '1H', '4H', '1D'];

// Generate demo backtest results
function generateBacktestEquity() {
  const data = [];
  let value = 10000;
  for (let i = 0; i < 90; i++) {
    value = value * (1 + (Math.random() - 0.47) * 0.015);
    data.push({ day: i + 1, value: Math.round(value * 100) / 100 });
  }
  return data;
}

const demoEquity = generateBacktestEquity();

const monthlyReturns = [
  { month: 'Jan', return: 3.2 },
  { month: 'Feb', return: -1.1 },
  { month: 'Mar', return: 4.5 },
  { month: 'Apr', return: 2.1 },
  { month: 'May', return: -0.8 },
  { month: 'Jun', return: 3.7 },
];

export default function Backtesting() {
  const [selectedStrategy, setSelectedStrategy] = useState('Trend Following');
  const [selectedSymbol, setSelectedSymbol] = useState('BTC/USDT');
  const [selectedTimeframe, setSelectedTimeframe] = useState('4H');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-03-31');
  const [startingBalance, setStartingBalance] = useState(10000);
  const [riskPerTrade, setRiskPerTrade] = useState(0.5);
  const [fees, setFees] = useState(0.1);
  const [slippage, setSlippage] = useState(0.05);
  const [isRunning, setIsRunning] = useState(false);
  const [hasResults, setHasResults] = useState(true);

  const handleRunBacktest = () => {
    setIsRunning(true);
    setTimeout(() => {
      setIsRunning(false);
      setHasResults(true);
    }, 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Backtesting</h1>
        <p className="text-sm text-slate-400">Test strategies with historical data and realistic cost modeling</p>
      </div>

      {/* Configuration */}
      <GlassCard className="p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Backtest Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Strategy</label>
            <select
              value={selectedStrategy}
              onChange={(e) => setSelectedStrategy(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
            >
              {strategies.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Symbol</label>
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
            >
              {symbols.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Timeframe</label>
            <select
              value={selectedTimeframe}
              onChange={(e) => setSelectedTimeframe(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
            >
              {timeframes.map((tf) => <option key={tf} value={tf}>{tf}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Starting Balance ($)</label>
            <input
              type="number"
              value={startingBalance}
              onChange={(e) => setStartingBalance(Number(e.target.value))}
              className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Risk Per Trade (%)</label>
            <input
              type="number"
              value={riskPerTrade}
              onChange={(e) => setRiskPerTrade(Number(e.target.value))}
              step={0.1}
              className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Fees (%) / Slippage (%)</label>
            <div className="flex gap-2">
              <input
                type="number"
                value={fees}
                onChange={(e) => setFees(Number(e.target.value))}
                step={0.01}
                className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
              />
              <input
                type="number"
                value={slippage}
                onChange={(e) => setSlippage(Number(e.target.value))}
                step={0.01}
                className="w-full rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
              />
            </div>
          </div>
        </div>
        <div className="mt-4 flex justify-end">
          <button
            onClick={handleRunBacktest}
            disabled={isRunning}
            className="flex items-center gap-2 rounded-lg bg-emerald-500 px-6 py-2.5 text-sm font-semibold text-white hover:bg-emerald-400 disabled:opacity-50 transition-colors"
          >
            <Play className="h-4 w-4" />
            {isRunning ? 'Running...' : 'Run Backtest'}
          </button>
        </div>
      </GlassCard>

      {hasResults && (
        <>
          {/* Results Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard title="Total Return" value="+12.4%" change={12.4} icon={<TrendingUp className="h-4 w-4" />} trend="up" />
            <MetricCard title="Win Rate" value="58.3%" change={2.1} icon={<Target className="h-4 w-4" />} trend="up" />
            <MetricCard title="Profit Factor" value="1.67" icon={<BarChart3 className="h-4 w-4" />} />
            <MetricCard title="Max Drawdown" value="-4.2%" change={-0.5} icon={<TrendingDown className="h-4 w-4" />} trend="down" />
          </div>

          {/* Equity Curve */}
          <GlassCard className="p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Equity Curve</h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={demoEquity}>
                  <defs>
                    <linearGradient id="backtestGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} tickFormatter={(v) => `$${(v / 1000).toFixed(1)}k`} />
                  <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }} />
                  <Area type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} fill="url(#backtestGradient)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>

          {/* Detailed Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <GlassCard className="p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Performance Metrics</h2>
              <div className="space-y-2">
                {[
                  { label: 'Net Profit', value: '+$1,240.00' },
                  { label: 'Annualized Return', value: '+54.8%' },
                  { label: 'Sharpe Ratio', value: '1.82' },
                  { label: 'Sortino Ratio', value: '2.34' },
                  { label: 'Calmar Ratio', value: '3.12' },
                  { label: 'Expectancy', value: '+$45.20' },
                  { label: 'Avg Win', value: '+$128.50' },
                  { label: 'Avg Loss', value: '-$78.30' },
                  { label: 'Largest Win', value: '+$342.00' },
                  { label: 'Largest Loss', value: '-$156.00' },
                  { label: 'Avg Holding Time', value: '4h 23m' },
                  { label: 'Total Trades', value: '28' },
                ].map((item) => (
                  <div key={item.label} className="flex justify-between text-sm py-1.5 border-b border-slate-800/50">
                    <span className="text-slate-400">{item.label}</span>
                    <span className="font-semibold text-white">{item.value}</span>
                  </div>
                ))}
              </div>
            </GlassCard>

            <GlassCard className="p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Monthly Returns</h2>
              <div className="space-y-2">
                {monthlyReturns.map((m) => (
                  <div key={m.month} className="flex items-center gap-3">
                    <span className="text-sm text-slate-400 w-8">{m.month}</span>
                    <div className="flex-1 h-6 rounded bg-slate-800/50 overflow-hidden">
                      <div
                        className={`h-full rounded ${m.return >= 0 ? 'bg-emerald-500' : 'bg-red-500'}`}
                        style={{ width: `${Math.abs(m.return) * 15}%` }}
                      />
                    </div>
                    <span className={`text-sm font-semibold w-16 text-right ${m.return >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {m.return >= 0 ? '+' : ''}{m.return}%
                    </span>
                  </div>
                ))}
              </div>
            </GlassCard>
          </div>
        </>
      )}
    </div>
  );
}
