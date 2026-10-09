import { motion } from 'framer-motion';

interface ConfidenceMeterProps {
  value: number;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export default function ConfidenceMeter({ value, label, size = 'md', showLabel = true }: ConfidenceMeterProps) {
  const clampedValue = Math.min(100, Math.max(0, value));
  
  const getColor = (v: number) => {
    if (v >= 70) return 'from-emerald-500 to-emerald-400';
    if (v >= 50) return 'from-amber-500 to-amber-400';
    return 'from-red-500 to-red-400';
  };

  const getTextColor = (v: number) => {
    if (v >= 70) return 'text-emerald-400';
    if (v >= 50) return 'text-amber-400';
    return 'text-red-400';
  };

  const heights = { sm: 'h-1.5', md: 'h-2.5', lg: 'h-4' };


  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs font-medium text-slate-400">{label || 'Confidence'}</span>
          <span className={`text-xs font-bold ${getTextColor(clampedValue)}`}>
            {clampedValue.toFixed(0)}%
          </span>
        </div>
      )}
      <div className={`w-full rounded-full bg-slate-800 ${heights[size]}`}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${clampedValue}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={`rounded-full bg-gradient-to-r ${getColor(clampedValue)} ${heights[size]}`}
        />
      </div>
    </div>
  );
}
