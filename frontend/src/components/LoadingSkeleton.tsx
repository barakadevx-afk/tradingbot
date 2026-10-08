interface LoadingSkeletonProps {
  className?: string;
  lines?: number;
}

export default function LoadingSkeleton({ className = '', lines = 1 }: LoadingSkeletonProps) {
  if (lines > 1) {
    return (
      <div className={`space-y-3 ${className}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className="h-4 rounded bg-slate-800/50 animate-pulse"
            style={{ width: `${100 - i * 10}%` }}
          />
        ))}
      </div>
    );
  }

  return (
    <div className={`h-4 rounded bg-slate-800/50 animate-pulse ${className}`} />
  );
}

export function CardSkeleton() {
  return (
    <div className="rounded-xl border border-slate-800/50 bg-slate-900/50 p-4 animate-pulse">
      <div className="h-3 w-24 rounded bg-slate-800/50 mb-3" />
      <div className="h-8 w-32 rounded bg-slate-800/50 mb-2" />
      <div className="h-3 w-20 rounded bg-slate-800/50" />
    </div>
  );
}

export function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          <div className="h-4 w-20 rounded bg-slate-800/50 animate-pulse" />
          <div className="h-4 w-16 rounded bg-slate-800/50 animate-pulse" />
          <div className="h-4 w-24 rounded bg-slate-800/50 animate-pulse" />
          <div className="h-4 w-16 rounded bg-slate-800/50 animate-pulse" />
          <div className="h-4 w-20 rounded bg-slate-800/50 animate-pulse" />
        </div>
      ))}
    </div>
  );
}
