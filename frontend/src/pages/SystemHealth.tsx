import { useCallback, useEffect, useState } from 'react';
import axios from 'axios';
import { Activity, AlertTriangle, Database, RefreshCw, Server, Shield } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import api from '../services/api';
import { useAuthStore } from '../store/authStore';

interface HealthResponse {
  services: Record<string, { status: string }>;
  timestamp: string;
}

const isAdminRole = (role?: string) => role === 'ADMIN' || role === 'SUPER_ADMIN';

export default function SystemHealth() {
  const user = useAuthStore((state) => state.user);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchHealth = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await api.get<HealthResponse>('/admin/system/health');
      setHealth(response.data);
      setError('');
    } catch (cause: unknown) {
      const detail = axios.isAxiosError<{ detail?: unknown }>(cause)
        ? cause.response?.data?.detail
        : undefined;
      setError(
        typeof detail === 'string'
          ? detail
          : cause instanceof Error
            ? cause.message
            : 'Unable to load system health.',
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAdminRole(user?.role)) {
      void fetchHealth();
    }
  }, [fetchHealth, user?.role]);

  if (!isAdminRole(user?.role)) {
    return (
      <GlassCard className="p-6">
        <div className="flex items-center gap-3 text-amber-300">
          <Shield className="h-5 w-5" />
          <p>Administrator access is required to view system health.</p>
        </div>
      </GlassCard>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold text-white">
            <Activity className="h-6 w-6 text-cyan-400" />
            System Health
          </h1>
          <p className="text-sm text-slate-400">Live status reported by the API and database health check</p>
        </div>
        <button
          onClick={() => void fetchHealth()}
          disabled={isLoading}
          className="flex items-center justify-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition-colors hover:bg-slate-800 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error && (
        <div role="alert" className="flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {health && (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {Object.entries(health.services).map(([name, service]) => (
              <GlassCard key={name} className="flex items-center justify-between p-5">
                <div className="flex items-center gap-3">
                  {name === 'database'
                    ? <Database className="h-5 w-5 text-cyan-400" />
                    : <Server className="h-5 w-5 text-purple-400" />}
                  <span className="capitalize text-white">{name}</span>
                </div>
                <StatusBadge status={service.status.toUpperCase()} />
              </GlassCard>
            ))}
          </div>
          <p className="text-xs text-slate-500">
            Last checked {new Date(health.timestamp).toLocaleString()}
          </p>
        </>
      )}

      {!health && isLoading && <p className="text-sm text-slate-400">Checking system health...</p>}
    </div>
  );
}
