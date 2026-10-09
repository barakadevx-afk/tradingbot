import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Shield,
  Users,
  Activity,
  Server,
  Database,
  Cpu,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  Lock,
  Mail,
  LogOut,
  RefreshCw,
  BarChart3,
  Settings,
  Bell,
  Eye,
  Trash2,
  Edit,
} from 'lucide-react';
import GlassCard from '../components/GlassCard';
import MetricCard from '../components/MetricCard';
import StatusBadge from '../components/StatusBadge';
import { useAuthStore } from '../store/authStore';

const ADMIN_EMAIL = 'barakatrader@gmail.com';
const ADMIN_PASSWORD = 'Baraka@2050!!!';

interface SystemService {
  name: string;
  status: string;
  latency: number;
  icon: React.ReactNode;
}

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export default function AdminDashboard() {
  const { user, logout } = useAuthStore();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({
    total_users: 0,
    active_users: 0,
    total_signals: 0,
    total_trades: 0,
    total_orders: 0,
    open_positions: 0,
  });
  const [users, setUsers] = useState<User[]>([]);
  const [services, setServices] = useState<SystemService[]>([]);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (isAuthenticated) {
      fetchStats();
      fetchUsers();
      fetchSystemHealth();
    }
  }, [isAuthenticated]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (email === ADMIN_EMAIL && password === ADMIN_PASSWORD) {
      setIsAuthenticated(true);
      setError('');
    } else {
      setError('Invalid admin credentials');
    }
    setIsLoading(false);
  };

  const fetchStats = async () => {
    setStats({
      total_users: 1247,
      active_users: 892,
      total_signals: 15420,
      total_trades: 3891,
      total_orders: 4102,
      open_positions: 18,
    });
  };

  const fetchUsers = async () => {
    setUsers([
      { id: '1', email: 'admin@baraka.ai', full_name: 'Admin User', role: 'SUPER_ADMIN', is_active: true, created_at: '2024-01-01' },
      { id: '2', email: 'trader@baraka.ai', full_name: 'Pro Trader', role: 'TRADER', is_active: true, created_at: '2024-02-15' },
      { id: '3', email: 'analyst@baraka.ai', full_name: 'Market Analyst', role: 'ANALYST', is_active: true, created_at: '2024-03-10' },
      { id: '4', email: 'viewer@baraka.ai', full_name: 'Read Only', role: 'VIEWER', is_active: false, created_at: '2024-04-05' },
    ]);
  };

  const fetchSystemHealth = async () => {
    setServices([
      { name: 'Frontend', status: 'HEALTHY', latency: 12, icon: <Server className="h-4 w-4" /> },
      { name: 'Backend API', status: 'HEALTHY', latency: 45, icon: <Server className="h-4 w-4" /> },
      { name: 'Database', status: 'HEALTHY', latency: 8, icon: <Database className="h-4 w-4" /> },
      { name: 'Redis', status: 'HEALTHY', latency: 2, icon: <Database className="h-4 w-4" /> },
      { name: 'Market Feed', status: 'HEALTHY', latency: 120, icon: <Activity className="h-4 w-4" /> },
      { name: 'AI Engine', status: 'HEALTHY', latency: 250, icon: <Cpu className="h-4 w-4" /> },
      { name: 'Risk Engine', status: 'HEALTHY', latency: 5, icon: <Shield className="h-4 w-4" /> },
      { name: 'Execution Engine', status: 'HEALTHY', latency: 15, icon: <Activity className="h-4 w-4" /> },
    ]);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setEmail('');
    setPassword('');
    logout();
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <div className="text-center mb-8">
            <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500 to-cyan-500 mb-4">
              <Shield className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
            <p className="text-sm text-slate-400 mt-1">BARAKA AI Management Console</p>
          </div>

          <GlassCard className="p-6">
            <form onSubmit={handleLogin} className="space-y-4">
              {error && (
                <div className="flex items-center gap-2 rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-400">
                  <AlertTriangle className="h-4 w-4" />
                  {error}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">Admin Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-900/50 pl-10 pr-4 py-2.5 text-white placeholder-slate-500 focus:border-purple-500 focus:outline-none"
                    placeholder="admin@baraka.ai"
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
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full rounded-lg border border-slate-700 bg-slate-900/50 pl-10 pr-4 py-2.5 text-white placeholder-slate-500 focus:border-purple-500 focus:outline-none"
                    placeholder="Enter admin password"
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Shield className="h-6 w-6 text-purple-400" />
            Admin Dashboard
          </h1>
          <p className="text-sm text-slate-400">BARAKA AI Management Console</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm text-slate-400">{ADMIN_EMAIL}</span>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-800 pb-2">
        {[
          { id: 'overview', label: 'Overview', icon: BarChart3 },
          { id: 'users', label: 'Users', icon: Users },
          { id: 'system', label: 'System', icon: Server },
          { id: 'settings', label: 'Settings', icon: Settings },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard title="Total Users" value={stats.total_users.toLocaleString()} change={12.5} icon={<Users className="h-4 w-4" />} trend="up" />
            <MetricCard title="Active Users" value={stats.active_users.toLocaleString()} change={8.3} icon={<Users className="h-4 w-4" />} trend="up" />
            <MetricCard title="Total Signals" value={stats.total_signals.toLocaleString()} change={23.1} icon={<Activity className="h-4 w-4" />} trend="up" />
            <MetricCard title="Total Trades" value={stats.total_trades.toLocaleString()} change={-2.4} icon={<TrendingUp className="h-4 w-4" />} trend="down" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <GlassCard className="p-6">
              <h2 className="text-lg font-semibold text-white mb-4">System Services</h2>
              <div className="space-y-3">
                {services.map((service) => (
                  <div key={service.name} className="flex items-center justify-between rounded-lg bg-slate-800/30 p-3">
                    <div className="flex items-center gap-3">
                      <div className="text-slate-400">{service.icon}</div>
                      <span className="text-sm font-medium text-white">{service.name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-slate-500">{service.latency}ms</span>
                      <StatusBadge status={service.status} size="sm" />
                    </div>
                  </div>
                ))}
              </div>
            </GlassCard>

            <GlassCard className="p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Recent Activity</h2>
              <div className="space-y-3">
                {[
                  { action: 'New user registered', time: '2 min ago', type: 'info' },
                  { action: 'High-confidence signal generated', time: '5 min ago', type: 'success' },
                  { action: 'Risk limit warning', time: '12 min ago', type: 'warning' },
                  { action: 'Model drift detected', time: '1 hour ago', type: 'warning' },
                  { action: 'Kill switch tested', time: '3 hours ago', type: 'info' },
                ].map((activity, i) => (
                  <div key={i} className="flex items-center justify-between rounded-lg bg-slate-800/30 p-3">
                    <div className="flex items-center gap-3">
                      {activity.type === 'success' ? (
                        <CheckCircle className="h-4 w-4 text-emerald-400" />
                      ) : activity.type === 'warning' ? (
                        <AlertTriangle className="h-4 w-4 text-amber-400" />
                      ) : (
                        <Activity className="h-4 w-4 text-blue-400" />
                      )}
                      <span className="text-sm text-slate-300">{activity.action}</span>
                    </div>
                    <span className="text-xs text-slate-500">{activity.time}</span>
                  </div>
                ))}
              </div>
            </GlassCard>
          </div>
        </div>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <GlassCard className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/50">
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">User</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Role</th>
                  <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-slate-500">Status</th>
                  <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Created</th>
                  <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3">
                      <div>
                        <p className="text-sm font-medium text-white">{u.full_name}</p>
                        <p className="text-xs text-slate-500">{u.email}</p>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`text-xs font-semibold px-2 py-1 rounded ${
                        u.role === 'SUPER_ADMIN' ? 'bg-purple-500/10 text-purple-400' :
                        u.role === 'ADMIN' ? 'bg-red-500/10 text-red-400' :
                        u.role === 'TRADER' ? 'bg-emerald-500/10 text-emerald-400' :
                        u.role === 'ANALYST' ? 'bg-cyan-500/10 text-cyan-400' :
                        'bg-slate-500/10 text-slate-400'
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <StatusBadge status={u.is_active ? 'HEALTHY' : 'OFFLINE'} size="sm" />
                    </td>
                    <td className="px-4 py-3 text-right text-xs text-slate-500">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button className="rounded p-1.5 text-slate-500 hover:text-white hover:bg-slate-800 transition-colors">
                          <Eye className="h-3.5 w-3.5" />
                        </button>
                        <button className="rounded p-1.5 text-slate-500 hover:text-white hover:bg-slate-800 transition-colors">
                          <Edit className="h-3.5 w-3.5" />
                        </button>
                        <button className="rounded p-1.5 text-slate-500 hover:text-red-400 hover:bg-slate-800 transition-colors">
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

      {/* System Tab */}
      {activeTab === 'system' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {services.map((service) => (
              <GlassCard key={service.name} className="p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="text-slate-400">{service.icon}</div>
                  <h3 className="text-sm font-semibold text-white">{service.name}</h3>
                </div>
                <div className="flex items-center justify-between">
                  <StatusBadge status={service.status} size="sm" />
                  <span className="text-xs text-slate-500">{service.latency}ms</span>
                </div>
              </GlassCard>
            ))}
          </div>
        </div>
      )}

      {/* Settings Tab */}
      {activeTab === 'settings' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <GlassCard className="p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Risk Configuration</h2>
            <div className="space-y-3">
              {[
                { label: 'Risk Per Trade', value: '0.5%' },
                { label: 'Max Daily Loss', value: '3%' },
                { label: 'Max Drawdown', value: '10%' },
                { label: 'Max Open Positions', value: '5' },
                { label: 'Kill Switch', value: 'Armed' },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between rounded-lg bg-slate-800/30 p-3">
                  <span className="text-sm text-slate-300">{item.label}</span>
                  <span className="text-sm font-semibold text-white">{item.value}</span>
                </div>
              ))}
            </div>
          </GlassCard>

          <GlassCard className="p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Exchange Connections</h2>
            <div className="space-y-3">
              {[
                { name: 'Binance', status: 'Connected', testnet: true },
                { name: 'Bybit', status: 'Disconnected', testnet: true },
                { name: 'Kraken', status: 'Disconnected', testnet: false },
                { name: 'Coinbase', status: 'Disconnected', testnet: false },
              ].map((exchange) => (
                <div key={exchange.name} className="flex items-center justify-between rounded-lg bg-slate-800/30 p-3">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-white">{exchange.name}</span>
                    {exchange.testnet && (
                      <span className="text-[10px] font-semibold text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded">TESTNET</span>
                    )}
                  </div>
                  <StatusBadge status={exchange.status === 'Connected' ? 'HEALTHY' : 'OFFLINE'} size="sm" />
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
}
