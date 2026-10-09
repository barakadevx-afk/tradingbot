import { useCallback, useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { AlertTriangle, RefreshCw, Search, Shield, Users as UsersIcon } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import api from '../services/api';
import { useAuthStore } from '../store/authStore';

interface ManagedUser {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
}

const isAdminRole = (role?: string) => role === 'ADMIN' || role === 'SUPER_ADMIN';

export default function Users() {
  const user = useAuthStore((state) => state.user);
  const [users, setUsers] = useState<ManagedUser[]>([]);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await api.get<ManagedUser[]>('/admin/users');
      setUsers(response.data);
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
            : 'Unable to load users.',
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAdminRole(user?.role)) {
      void fetchUsers();
    }
  }, [fetchUsers, user?.role]);

  const filteredUsers = useMemo(() => {
    const query = search.trim().toLowerCase();
    return users.filter((item) => {
      const matchesQuery = !query
        || item.email.toLowerCase().includes(query)
        || (item.full_name || '').toLowerCase().includes(query);
      return matchesQuery && (roleFilter === 'all' || item.role === roleFilter);
    });
  }, [roleFilter, search, users]);

  if (!isAdminRole(user?.role)) {
    return (
      <GlassCard className="p-6">
        <div className="flex items-center gap-3 text-amber-300">
          <Shield className="h-5 w-5" />
          <p>Administrator access is required to view user accounts.</p>
        </div>
      </GlassCard>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-bold text-white">
            <UsersIcon className="h-6 w-6 text-cyan-400" />
            User Management
          </h1>
          <p className="text-sm text-slate-400">Registered accounts and their current access roles</p>
        </div>
        <button
          onClick={() => void fetchUsers()}
          disabled={isLoading}
          className="flex items-center justify-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 transition-colors hover:bg-slate-800 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <GlassCard className="p-4">
        <div className="flex flex-col gap-4 md:flex-row">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search name or email..."
              className="w-full rounded-lg border border-slate-700 bg-slate-900/50 py-2 pl-10 pr-4 text-sm text-white placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
            />
          </div>
          <select
            value={roleFilter}
            onChange={(event) => setRoleFilter(event.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-cyan-500 focus:outline-none"
            aria-label="Filter users by role"
          >
            <option value="all">All roles</option>
            <option value="SUPER_ADMIN">Super Admin</option>
            <option value="ADMIN">Admin</option>
            <option value="TRADER">Trader</option>
            <option value="ANALYST">Analyst</option>
            <option value="VIEWER">Viewer</option>
          </select>
        </div>
      </GlassCard>

      {error && (
        <div role="alert" className="flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      <GlassCard className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[600px]">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/50">
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">User</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Role</th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-slate-500">Status</th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filteredUsers.map((item) => (
                <tr key={item.id} className="text-slate-300 transition-colors hover:bg-slate-800/30">
                  <td className="px-4 py-3">
                    <p className="text-sm font-medium text-white">{item.full_name || '—'}</p>
                    <p className="text-xs text-slate-500">{item.email}</p>
                  </td>
                  <td className="px-4 py-3 text-sm">{item.role}</td>
                  <td className="px-4 py-3 text-center">
                    <StatusBadge status={item.is_active ? 'HEALTHY' : 'OFFLINE'} size="sm" />
                  </td>
                  <td className="px-4 py-3 text-right text-xs text-slate-500">
                    {new Date(item.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
              {!isLoading && filteredUsers.length === 0 && (
                <tr>
                  <td className="px-4 py-6 text-center text-sm text-slate-400" colSpan={4}>
                    {error ? 'User data is unavailable.' : 'No users match these filters.'}
                  </td>
                </tr>
              )}
              {isLoading && (
                <tr>
                  <td className="px-4 py-6 text-center text-sm text-slate-400" colSpan={4}>
                    Loading users...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </GlassCard>
    </div>
  );
}
