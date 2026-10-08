import { motion } from 'framer-motion';
import { Activity, Server, Database, Wifi, Cpu, HardDrive, Clock, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import type { SystemHealth } from '../types';

const systemServices: SystemHealth[] = [
  { service: 'Frontend', status: 'HEALTHY', latency_ms: 12, last_heartbeat: new Date().toISOString(), cpu_percent: 15, memory_percent: 32 },
  { service: 'Backend API', status: 'HEALTHY', latency_ms: 45, last_heartbeat: new Date().toISOString(), cpu_percent: 28, memory_percent: 45 },
  { service: 'PostgreSQL', status: 'HEALTHY', latency_ms: 8, last_heartbeat: new Date().toISOString(), cpu_percent: 22, memory_percent: 55 },
  { service: 'Redis', status: 'HEALTHY', latency_ms: 2, last_heartbeat: new Date().toISOString(), cpu_percent: 8, memory_percent: 18 },
  { service: 'Market Feed', status: 'HEALTHY', latency_ms: 120, last_heartbeat: new Date().toISOString(), cpu_percent: 35, memory_percent: 42 },
  { service: 'Exchange REST', status: 'HEALTHY', latency_ms: 85, last_heartbeat: new Date().toISOString(), cpu_percent: 12, memory_percent: 25 },
  { service: 'Exchange WebSocket', status: 'HEALTHY', latency_ms: 95, last_heartbeat: new Date().toISOString(), cpu_percent: 18, memory_percent: 30 },
  { service: 'AI Engine', status: 'HEALTHY', latency_ms: 250, last_heartbeat: new Date().toISOString(), cpu_percent: 55, memory_percent: 68 },
  { service: 'Risk Engine', status: 'HEALTHY', latency_ms: 5, last_heartbeat: new Date().toISOString(), cpu_percent: 10, memory_percent: 22 },
  { service: 'Execution Engine', status: 'HEALTHY', latency_ms: 15, last_heartbeat: new Date().toISOString(), cpu_percent: 20, memory_percent: 35 },
  { service: 'Worker Queue', status: 'WARNING', latency_ms: 500, last_heartbeat: new Date(Date.now() - 30000).toISOString(), cpu_percent: 72, memory_percent: 78 },
];

const dataQuality = [
  { label: 'Last Market Update', value: '2 seconds ago', status: 'ok' },
  { label: 'WebSocket Latency', value: '95ms', status: 'ok' },
  { label: 'Missing Candles', value: '0', status: 'ok' },
  { label: 'Duplicate Candles', value: '0', status: 'ok' },
  { label: 'Exchange Errors', value: '0', status: 'ok' },
  { label: 'Feed Reconnections', value: '2 (24h)', status: 'ok' },
  { label: 'Stale Symbols', value: '0', status: 'ok' },
];

export default function SystemHealth() {
  const healthyCount = systemServices.filter((s) => s.status === 'HEALTHY').length;
  const warningCount = systemServices.filter((s) => s.status === 'WARNING').length;
  const criticalCount = systemServices.filter((s) => s.status === 'CRITICAL').length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">System Health</h1>
        <p className="text-sm text-slate-400">Monitor all system components and services</p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <GlassCard className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10">
              <CheckCircle className="h-5 w-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{healthyCount}</p>
              <p className="text-xs text-slate-500">Healthy</p>
            </div>
          </div>
        </GlassCard>
        <GlassCard className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-500/10">
              <AlertTriangle className="h-5 w-5 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{warningCount}</p>
              <p className="text-xs text-slate-500">Warning</p>
            </div>
          </div>
        </GlassCard>
        <GlassCard className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-red-500/10">
              <XCircle className="h-5 w-5 text-red-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{criticalCount}</p>
              <p className="text-xs text-slate-500">Critical</p>
            </div>
          </div>
        </GlassCard>
        <GlassCard className="p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-cyan-500/10">
              <Activity className="h-5 w-5 text-cyan-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{systemServices.length}</p>
              <p className="text-xs text-slate-500">Total Services</p>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {systemServices.map((service, i) => (
          <motion.div
            key={service.service}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.03 }}
          >
            <GlassCard className="p-4" hover>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Server className="h-4 w-4 text-slate-500" />
                  <h3 className="text-sm font-semibold text-white">{service.service}</h3>
                </div>
                <StatusBadge status={service.status} size="sm" />
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">Latency</span>
                  <span className="font-semibold text-white">{service.latency_ms}ms</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">CPU</span>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 rounded-full bg-slate-800">
                      <div
                        className={h-full rounded-full }
                        style={{ width: ${service.cpu_percent}% }}
                      />
                    </div>
                    <span className="font-semibold text-white w-8 text-right">{service.cpu_percent}%</span>
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Memory</span>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 rounded-full bg-slate-800">
                      <div
                        className={h-full rounded-full }
                        style={{ width: ${service.memory_percent}% }}
                      />
                    </div>
                    <span className="font-semibold text-white w-8 text-right">{service.memory_percent}%</span>
                  </div>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Last Heartbeat</span>
                  <span className="font-semibold text-white">
                    {new Date(service.last_heartbeat).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* Data Quality */}
      <GlassCard className="p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Data Quality Monitor</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {dataQuality.map((item) => (
            <div key={item.label} className="flex items-center justify-between rounded-lg bg-slate-800/30 p-3">
              <span className="text-sm text-slate-400">{item.label}</span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-white">{item.value}</span>
                <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
              </div>
            </div>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}
