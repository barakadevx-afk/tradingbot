import { SignalType, SystemStatus, ModelStatus } from '../types';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md' | 'lg';
}

const signalColors: Record<SignalType, string> = {
  BUY: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  SELL: 'bg-red-500/10 text-red-400 border-red-500/20',
  HOLD: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
};

const systemColors: Record<SystemStatus, string> = {
  HEALTHY: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  WARNING: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  CRITICAL: 'bg-red-500/10 text-red-400 border-red-500/20',
  OFFLINE: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
};

const modelColors: Record<ModelStatus, string> = {
  DRAFT: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  TESTING: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  APPROVED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  PRODUCTION: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
  RETIRED: 'bg-red-500/10 text-red-400 border-red-500/20',
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-[10px]',
  md: 'px-2.5 py-1 text-xs',
  lg: 'px-3 py-1.5 text-sm',
};

export default function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  let colors = 'bg-slate-500/10 text-slate-400 border-slate-500/20';

  if (status in signalColors) {
    colors = signalColors[status as SignalType];
  } else if (status in systemColors) {
    colors = systemColors[status as SystemStatus];
  } else if (status in modelColors) {
    colors = modelColors[status as ModelStatus];
  }

  return (
    <span
      className={`inline-flex items-center rounded-full border font-semibold uppercase tracking-wider ${colors} ${sizeClasses[size]}`}
    >
      {status}
    </span>
  );
}
