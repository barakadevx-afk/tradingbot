import { FormEvent, useCallback, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle,
  Cpu,
  Database,
  Lock,
  LogOut,
  Mail,
  RefreshCw,
  Server,
  Shield,
  Users,
} from 'lucide-react';
import GlassCard from '../components/GlassCard';
import MetricCard from '../components/MetricCard';
import StatusBadge from '../components/StatusBadge';
import api from '../services/api';
import { useAuthStore } from '../store/authStore';

interface AdminStats {
  total_users: number;
  active_users: number;
  total_signals: number;
  total_trades: number;
  total_orders: number;
  open_positions: number;
  system_status: string;
}

interface AdminUser {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
}

interface SystemHealth {
  services: Record<string, { status: string }>;
  timestamp: string;
}

const isAdminRole = (role?: string) => role === 'ADMIN' || role === 'SUPER_ADMIN';

export default function AdminDashboard() {
  const { user, isAuthenticated, login, logout } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'system'>('overview');

  const fetchDashboard = useCallback(async () => {
    const [statsResponse, usersResponse, healthResponse] = await Promise.all([
      api.get<AdminStats>('/admin/stats'),
      api.get<AdminUser[]>('/admin/users'),
      api.get<SystemHealth>('/admin/system/health'),
    ]);
    setStats(statsResponse.data);
    setUsers(usersResponse.data);
    setHealth(healthResponse.data);
    setError('');
  }, []);

  useEffect(() => {
    if (!isAuthenticated || !isAdminRole(user?.role)) return;
    fetchDashboard().catch((cause: unknown) => {
      setError(cause instanceof Error ? cause.message : 'Unable to load administrator data.');
    });
  }, [fetchDashboard, isAuthenticated, user?.role]);

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await login(email, password);
      const authenticatedUser = useAuthStore.getState().user;
      if (!isAdminRole(authenticatedUser?.role)) {
        logout();
        setError('This account does not have administrator access.');
      }
    } catch (cause: unknown) {
      setError(cause instanceof Error ? cause.message : 'Unable to sign in.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    setStats(null);
    setUsers([]);
    setHealth(null);
  };

  if (!isAuthenticated || !isAdminRole(user?.role)) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <div className="text-center mb-8">
            <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 mb-4">
              <img src="/logo.svg" alt="BARAKA TRADING BOT" className="w-10 h-10" />
            </div>
            <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
            <p className="text-sm text-slate-400 mt-1">Sign in with an administrator account</p>
          </div>

          <GlassCard className="p-6">
            <form onSubmit={handleLogin} className="space-y-4">
              {error && (
                <div role="alert" className="flex items-center gap-2 rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-400">
                  <AlertTriangle className="h-4 w-4 shrink-0" />
                  {error}
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">Admin Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                  <input
                    type="email"
                    autoComplete="username"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-900/50 pl-10 pr-4 py-2.5 text-white placeholder-slate-500 focus:border-purple-500 focus:outline-none"
                    placeholder="admin@example.com"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                  <input
                    type="password"
                    autoComplete="current-password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-900/50 pl-10 pr-4 py-2.5 text-white placeholder-slate-500 focus:border-purple-500 focus:outline-none"
                    placeholder="Enter password"
                    required
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-purple-500 to-cyan-500 py-2.5 font-semibold text-white hover:opacity-90 disabled:opacity-50 transition-opacity"
              >
                {isLoading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Shield className="h-4 w-4" />}
                {isLoading ? 'Authenticating...' : 'Access Dashboard'}
              </button>
            </form>
          </GlassCard>
        </motion.div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'system', label: 'System', icon: Activity },
  ] as const;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Shield className="h-6 w-6 text-purple-400" />
            Admin Dashboard
          </h1>
          <p className="text-sm text-slate-400">BARAKA AI Management Console</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-400">{user.email}</span>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </div>

      <div className="flex gap-2 border-b border-slate-800 pb-2">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm transition-colors ${
              activeTab === id ? 'bg-purple-500/20 text-purple-300' : 'text-slate-400 hover:bg-slate-800'
            }`}
          >
            <Icon className="h-4 w-4" />
            {label}
          </button>
        ))}
      </div>

      {error && (
        <div role="alert" className="flex items-center justify-between gap-4 rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-400">
          <span className="flex items-center gap-2"><AlertTriangle className="h-4 w-4 shrink-0" />{error}</span>
          <button onClick={() => void fetchDashboard().catch((cause: unknown) => setError(cause instanceof Error ? cause.message : 'Unable to load administrator data.'))} className="shrink-0 underline">Retry</button>
        </div>
      )}

      {activeTab === 'overview' && (
        stats ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
            <MetricCard title="Total Users" value={stats.total_users.toLocaleString()} icon={<Users className="h-5 w-5" />} />
            <MetricCard title="Active Users" value={stats.active_users.toLocaleString()} icon={<Activity className="h-5 w-5" />} />
            <MetricCard title="Total Signals" value={stats.total_signals.toLocaleString()} icon={<BarChart3 className="h-5 w-5" />} />
            <MetricCard title="Total Trades" value={stats.total_trades.toLocaleString()} icon={<Activity className="h-5 w-5" />} />
            <MetricCard title="Total Orders" value={stats.total_orders.toLocaleString()} icon={<Database className="h-5 w-5" />} />
            <MetricCard title="Open Positions" value={stats.open_positions.toLocaleString()} icon={<Cpu className="h-5 w-5" />} />
            <GlassCard className="p-5 sm:col-span-2 xl:col-span-3">
              <div className="flex items-center gap-3">
                {stats.system_status === 'healthy' ? <CheckCircle className="h-5 w-5 text-emerald-400" /> : <AlertTriangle className="h-5 w-5 text-amber-400" />}
                <div>
                  <p className="font-medium text-white">Platform status</p>
                  <p className="text-sm text-slate-400 capitalize">{stats.system_status}</p>
                </div>
              </div>
            </GlassCard>
          </div>
        ) : !error && <p className="text-sm text-slate-400">Loading administrator data...</p>
      )}

      {activeTab === 'users' && (
        <GlassCard className="overflow-x-auto">
          <table className="w-full min-w-[600px] text-left text-sm">
            <thead className="text-slate-400 border-b border-slate-800">
              <tr><th className="p-4">User</th><th className="p-4">Role</th><th className="p-4">Status</th><th className="p-4">Created</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {users.map((item) => (
                <tr key={item.id} className="text-slate-300">
                  <td className="p-4"><span className="block text-white">{item.full_name || '—'}</span><span className="text-xs text-slate-500">{item.email}</span></td>
                  <td className="p-4">{item.role}</td>
                  <td className="p-4"><StatusBadge status={item.is_active ? 'HEALTHY' : 'OFFLINE'} /></td>
                  <td className="p-4">{new Date(item.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
              {users.length === 0 && <tr><td className="p-4 text-slate-400" colSpan={4}>No users found.</td></tr>}
            </tbody>
          </table>
        </GlassCard>
      )}

      {activeTab === 'system' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {health ? Object.entries(health.services).map(([name, service]) => (
            <GlassCard key={name} className="p-5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                {name === 'database' ? <Database className="h-5 w-5 text-cyan-400" /> : <Server className="h-5 w-5 text-purple-400" />}
                <span className="text-white capitalize">{name}</span>
              </div>
              <StatusBadge status={service.status.toUpperCase()} />
            </GlassCard>
          )) : !error && <p className="text-sm text-slate-400">Loading system health...</p>}
          {health && <p className="sm:col-span-2 text-xs text-slate-500">Checked {new Date(health.timestamp).toLocaleString()}</p>}
        </div>
      )}
    </div>
  );
}
