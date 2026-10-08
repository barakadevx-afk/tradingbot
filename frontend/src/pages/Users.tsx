import { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, Shield, Edit, Trash2, Plus, Search } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import type { User } from '../types';

const demoUsers: (User & { status: string })[] = [
  { id: 'user-001', email: 'admin@baraka.ai', full_name: 'Admin User', role: 'SUPER_ADMIN', is_active: true, is_2fa_enabled: true, created_at: '2024-01-01', updated_at: '2024-06-15', status: 'active' },
  { id: 'user-002', email: 'trader@baraka.ai', full_name: 'Pro Trader', role: 'TRADER', is_active: true, is_2fa_enabled: true, created_at: '2024-02-15', updated_at: '2024-06-20', status: 'active' },
  { id: 'user-003', email: 'analyst@baraka.ai', full_name: 'Market Analyst', role: 'ANALYST', is_active: true, is_2fa_enabled: false, created_at: '2024-03-10', updated_at: '2024-05-30', status: 'active' },
  { id: 'user-004', email: 'viewer@baraka.ai', full_name: 'Read Only', role: 'VIEWER', is_active: false, is_2fa_enabled: false, created_at: '2024-04-05', updated_at: '2024-04-05', status: 'inactive' },
];

const roleColors: Record<string, string> = {
  SUPER_ADMIN: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  ADMIN: 'bg-red-500/10 text-red-400 border-red-500/20',
  TRADER: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  ANALYST: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
  VIEWER: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
};

export default function Users() {
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');

  const filtered = demoUsers.filter((u) => {
    if (search && !u.email.toLowerCase().includes(search.toLowerCase()) && !u.full_name.toLowerCase().includes(search.toLowerCase())) return false;
    if (roleFilter !== 'all' && u.role !== roleFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">User Management</h1>
          <p className="text-sm text-slate-400">Manage users, roles, and permissions</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-400 transition-colors">
          <Plus className="h-4 w-4" />
          Add User
        </button>
      </div>

      {/* Filters */}
      <GlassCard className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search users..."
              className="w-full rounded-lg border border-slate-700 bg-slate-900/50 pl-10 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
            />
          </div>
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-emerald-500 focus:outline-none"
          >
            <option value="all">All Roles</option>
            <option value="SUPER_ADMIN">Super Admin</option>
            <option value="ADMIN">Admin</option>
            <option value="TRADER">Trader</option>
            <option value="ANALYST">Analyst</option>
            <option value="VIEWER">Viewer</option>
          </select>
        </div>
      </GlassCard>

      {/* Users Table */}
      <GlassCard className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-900/50">
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">User</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Role</th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-slate-500">2FA</th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-slate-500">Status</th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Created</th>
                <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {filtered.map((user) => (
                <tr key={user.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-slate-700 to-slate-600 text-sm font-bold text-white">
                        {user.full_name.charAt(0)}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-white">{user.full_name}</p>
                        <p className="text-xs text-slate-500">{user.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold }>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    {user.is_2fa_enabled ? (
                      <Shield className="h-4 w-4 text-emerald-400 mx-auto" />
                    ) : (
                      <Shield className="h-4 w-4 text-slate-600 mx-auto" />
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <StatusBadge status={user.is_active ? 'HEALTHY' : 'OFFLINE'} size="sm" />
                  </td>
                  <td className="px-4 py-3 text-right text-xs text-slate-500">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
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

      {/* Role Permissions */}
      <GlassCard className="p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Role Permissions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { role: 'SUPER_ADMIN', permissions: ['All permissions', 'User management', 'System configuration', 'Kill switch reset'] },
            { role: 'ADMIN', permissions: ['Strategy management', 'Model approval', 'Risk configuration', 'Audit logs'] },
            { role: 'TRADER', permissions: ['Paper trading', 'View signals', 'Manage own positions', 'View portfolio'] },
            { role: 'ANALYST', permissions: ['View all data', 'Run backtests', 'View analytics', 'Export reports'] },
            { role: 'VIEWER', permissions: ['View dashboard', 'View signals', 'View portfolio', 'Read-only access'] },
          ].map((r) => (
            <div key={r.role} className="rounded-lg bg-slate-800/30 p-4">
              <span className={inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold mb-3 }>
                {r.role}
              </span>
              <ul className="space-y-1">
                {r.permissions.map((p) => (
                  <li key={p} className="text-xs text-slate-400 flex items-center gap-2">
                    <span className="h-1 w-1 rounded-full bg-slate-600" />
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
