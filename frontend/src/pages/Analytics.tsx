import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Target, Calendar, Clock, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import GlassCard from '../components/GlassCard';
import MetricCard from '../components/MetricCard';

const weekdayData = [
  { day: 'Mon', pnl: 120 },
  { day: 'Tue', pnl: -45 },
  { day: 'Wed', pnl: 230 },
  { day: 'Thu', pnl: 89 },
  { day: 'Fri', pnl: -12 },
  { day: 'Sat', pnl: 167 },
  { day: 'Sun', pnl: 45 },
];

const hourlyData = [
  { hour: '00', trades: 3 },
  { hour: '04', trades: 1 },
  { hour: '08', trades: 5 },
  { hour: '12', trades: 8 },
  { hour: '16', trades: 6 },
  { hour: '20', trades: 4 },
];

const regimeData = [
  { name: 'TREND_UP', value: 35, color: '#10b981' },
  { name: 'TREND_DOWN', value: 20, color: '#ef4444' },
  { name: 'RANGE', value: 25, color: '#f59e0b' },
  { name: 'BREAKOUT', value: 12, color: '#22d3ee' },
  { name: 'UNCERTAIN', value: 8, color: '#64748b' },
];

const strategyData = [
  { name: 'Trend Following', return: 18.2, trades: 12 },
  { name: 'Breakout', return: 12.5, trades: 8 },
  { name: 'Pullback', return: 8.7, trades: 6 },
  { name: 'Mean Reversion', return: -2.1, trades: 4 },
];

export default function Analytics() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="text-sm text-slate-400">Performance analysis across multiple dimensions</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Win Rate" value="62.5%" change={3.2} icon={<Target className="h-4 w-4" />} trend="up" />
        <MetricCard title="Profit Factor" value="1.82" icon={<BarChart3 className="h-4 w-4" />} />
        <MetricCard title="Sharpe Ratio" value="1.67" icon={<TrendingUp className="h-4 w-4" />} />
        <MetricCard title="Max Drawdown" value="-4.2%" icon={<Activity className="h-4 w-4" />} trend="down" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance by Weekday */}
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Performance by Weekday</h2>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weekdayData}>
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }} />
                <Bar dataKey="pnl" radius={[4, 4, 0, 0]}>
                  {weekdayData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.pnl >= 0 ? '#10b981' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Performance by Hour */}
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Trading Activity by Hour</h2>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={hourlyData}>
                <XAxis dataKey="hour" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }} />
                <Line type="monotone" dataKey="trades" stroke="#22d3ee" strokeWidth={2} dot={{ fill: '#22d3ee', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Performance by Regime */}
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Performance by Market Regime</h2>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={regimeData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} paddingAngle={2} dataKey="value">
                  {regimeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 flex flex-wrap gap-3 justify-center">
            {regimeData.map((item) => (
              <div key={item.name} className="flex items-center gap-1.5 text-xs">
                <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-slate-400">{item.name}</span>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Performance by Strategy */}
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Performance by Strategy</h2>
          <div className="space-y-3">
            {strategyData.map((s) => (
              <div key={s.name} className="flex items-center gap-3">
                <span className="text-sm text-slate-300 w-32">{s.name}</span>
                <div className="flex-1 h-6 rounded bg-slate-800/50 overflow-hidden">
                  <div
                    className={`h-full rounded ${s.return >= 0 ? 'bg-emerald-500' : 'bg-red-500'}`}
                    style={{ width: `${Math.abs(s.return) * 4}%` }}
                  />
                </div>
                <span className={`text-sm font-semibold w-16 text-right ${s.return >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {s.return >= 0 ? '+' : ''}{s.return}%
                </span>
                <span className="text-xs text-slate-500 w-12 text-right">{s.trades} trades</span>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>

      {/* Best/Worst */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <GlassCard className="p-4">
          <p className="text-xs text-slate-500 mb-1">Best Strategy</p>
          <p className="text-lg font-bold text-emerald-400">Trend Following</p>
          <p className="text-xs text-slate-500">+18.2% return</p>
        </GlassCard>
        <GlassCard className="p-4">
          <p className="text-xs text-slate-500 mb-1">Worst Strategy</p>
          <p className="text-lg font-bold text-red-400">Mean Reversion</p>
          <p className="text-xs text-slate-500">-2.1% return</p>
        </GlassCard>
        <GlassCard className="p-4">
          <p className="text-xs text-slate-500 mb-1">Best Asset</p>
          <p className="text-lg font-bold text-emerald-400">BTC/USDT</p>
          <p className="text-xs text-slate-500">+24.5% return</p>
        </GlassCard>
        <GlassCard className="p-4">
          <p className="text-xs text-slate-500 mb-1">Worst Asset</p>
          <p className="text-lg font-bold text-red-400">DOGE/USDT</p>
          <p className="text-xs text-slate-500">-8.3% return</p>
        </GlassCard>
      </div>
    </div>
  );
}
