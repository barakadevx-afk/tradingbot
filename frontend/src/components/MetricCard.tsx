import { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  change?: number;
  changeLabel?: string;
  icon?: ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}

export default function MetricCard({
  title,
  value,
  change,
  changeLabel,
  icon,
  trend = 'neutral',
  className = '',
}: MetricCardProps) {
  const trendColor = trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-red-400' : 'text-slate-400';
  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`rounded-xl border border-slate-800/50 bg-slate-900/50 backdrop-blur-sm p-4 shadow-lg hover:border-slate-700/50 transition-all duration-300 ${className}`}
    >
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{title}</p>
        {icon && <div className="text-slate-500">{icon}</div>}
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      {change !== undefined && (
        <div className={`flex items-center gap-1 mt-1 text-xs ${trendColor}`}>
          {TrendIcon && <TrendIcon className="h-3 w-3" />}
          <span className="font-semibold">
            {change > 0 ? '+' : ''}{change.toFixed(2)}%
          </span>
          {changeLabel && <span className="text-slate-500">{changeLabel}</span>}
        </div>
      )}
    </motion.div>
  );
}
