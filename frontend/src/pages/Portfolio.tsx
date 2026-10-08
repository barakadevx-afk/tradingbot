import { motion } from 'framer-motion';
import { Briefcase, TrendingUp, TrendingDown, PieChart as PieIcon } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis } from 'recharts';
import GlassCard from '../components/GlassCard';
import MetricCard from '../components/MetricCard';

const allocationData = [
  { name: 'USDT', value: 8247.83, color: '#64748b' },
  { name: 'BTC', value: 1200, color: '#f7931a' },
  { name: 'ETH', value: 800, color: '#627eea' },
  { name: 'SOL', value: 200, color: '#9945ff' },
];

const drawdownData = [
  { date: 'Day 1', value: 0 },
  { date: 'Day 5', value: -0.5 },
  { date: 'Day 10', value: -1.2 },
  { date: 'Day 15', value: -0.8 },
  { date: 'Day 20', value: -1.8 },
  { date: 'Day 25', value: -0.3 },
  { date: 'Day 30', value: 0 },
];

const monthlyPnl = [
  { month: 'Jan', value: 120 },
  { month: 'Feb', value: -45 },
  { month: 'Mar', value: 230 },
  { month: 'Apr', value: 89 },
  { month: 'May', value: -12 },
  { month: 'Jun', value: 167 },
];

export default function Portfolio() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Portfolio</h1>
        <p className="text-sm text-slate-400">Portfolio overview and performance analytics</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Total Value" value="$10,247.83" change={2.48} icon={<Briefcase className="h-4 w-4" />} trend="up" />
        <MetricCard title="Cash" value="$8,247.83" icon={<Briefcase className="h-4 w-4" />} />
        <MetricCard title="Open Exposure" value="$2,000.00" icon={<TrendingUp className="h-4 w-4" />} />
        <MetricCard title="Unrealized P&L" value="+$100.00" change={1.0} icon={<TrendingUp className="h-4 w-4" />} trend="up" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Allocation */}
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Allocation</h2>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(value: number) => [`$${value.toFixed(2)}`, '']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-2">
            {allocationData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-slate-300">{item.name}</span>
                </div>
                <span className="font-semibold text-white">
                  {((item.value / 10247.83) * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Drawdown Chart */}
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Drawdown</h2>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={drawdownData}>
                <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="value" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Monthly P&L */}
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Monthly P&L</h2>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyPnl}>
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {monthlyPnl.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.value >= 0 ? '#10b981' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>

      {/* Holdings Table */}
      <GlassCard className="p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Holdings</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="pb-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Asset</th>
                <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Quantity</th>
                <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Price</th>
                <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Value</th>
                <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">P&L</th>
                <th className="pb-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Weight</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {[
                { asset: 'BTC', qty: '0.0178', price: 67432, value: 1200, pnl: 45.20, weight: 11.7 },
                { asset: 'ETH', qty: '0.2258', price: 3542, value: 800, pnl: 28.50, weight: 7.8 },
                { asset: 'SOL', qty: '1.121', price: 178.45, value: 200, pnl: -12.30, weight: 2.0 },
                { asset: 'USDT', qty: '8247.83', price: 1, value: 8247.83, pnl: 0, weight: 80.5 },
              ].map((h) => (
                <tr key={h.asset} className="hover:bg-slate-800/30">
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 text-xs font-bold text-slate-300">
                        {h.asset.charAt(0)}
                      </div>
                      <span className="text-sm font-medium text-white">{h.asset}</span>
                    </div>
                  </td>
                  <td className="py-3 text-right text-sm text-slate-300">{h.qty}</td>
                  <td className="py-3 text-right text-sm text-slate-300">${h.price.toLocaleString()}</td>
                  <td className="py-3 text-right text-sm font-semibold text-white">${h.value.toLocaleString()}</td>
                  <td className={`py-3 text-right text-sm font-semibold ${h.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {h.pnl >= 0 ? '+' : ''}${h.pnl.toFixed(2)}
                  </td>
                  <td className="py-3 text-right text-sm text-slate-300">{h.weight}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
