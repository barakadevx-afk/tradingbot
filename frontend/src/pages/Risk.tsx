import { useState } from 'react';
import { AlertTriangle, Save, RotateCcw } from 'lucide-react';
import GlassCard from '../components/GlassCard';

export default function Risk() {
  const [config, setConfig] = useState({
    risk_per_trade: 0.5,
    max_risk_per_trade: 1.0,
    max_daily_loss: 3.0,
    max_weekly_loss: 5.0,
    max_drawdown: 10.0,
    max_open_positions: 5,
    max_leverage: 1,
    max_portfolio_exposure: 80,
    max_symbol_exposure: 30,
    max_consecutive_losses: 5,
    min_confidence: 70,
    min_risk_reward: 1.5,
  });

  const [killSwitchActive, setKillSwitchActive] = useState(false);

  const handleChange = (key: string, value: number) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const riskMetrics = [
    { label: 'Daily Loss Used', value: 1.2, max: 3.0, color: 'emerald' },
    { label: 'Drawdown Used', value: 4.5, max: 10.0, color: 'amber' },
    { label: 'Exposure Used', value: 19.5, max: 80.0, color: 'emerald' },
    { label: 'Consecutive Losses', value: 1, max: 5, color: 'emerald' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Risk Management</h1>
          <p className="text-sm text-slate-400">Configure risk parameters and monitor exposure</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors">
            <RotateCcw className="h-4 w-4" />
            Reset Defaults
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-400 transition-colors">
            <Save className="h-4 w-4" />
            Save Changes
          </button>
        </div>
      </div>

      {/* Kill Switch */}
      <GlassCard className="p-6" glow="red">
        <div className="flex flex-col sm:flex-row sm:items-center gap-4">
          <div className="flex items-center gap-4 flex-1">
            <div className={`flex h-14 w-14 items-center justify-center rounded-xl ${
              killSwitchActive ? 'bg-red-500/20 text-red-400' : 'bg-slate-800 text-slate-500'
            }`}>
              <AlertTriangle className="h-7 w-7" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Emergency Kill Switch</h2>
              <p className="text-sm text-slate-400">
                {killSwitchActive
                  ? 'ACTIVE — All trading is blocked. New orders will be rejected.'
                  : 'Immediately blocks all new trades and cancels pending orders.'}
              </p>
            </div>
          </div>
          <button
            onClick={() => setKillSwitchActive(!killSwitchActive)}
            className={`rounded-xl px-6 py-3 font-bold text-sm uppercase tracking-wider transition-all ${
              killSwitchActive
                ? 'bg-red-500 text-white hover:bg-red-400 shadow-lg shadow-red-500/20'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700'
            }`}
          >
            {killSwitchActive ? 'Deactivate Kill Switch' : 'Activate Kill Switch'}
          </button>
        </div>
      </GlassCard>

      {/* Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {riskMetrics.map((metric) => (
          <GlassCard key={metric.label} className="p-4">
            <p className="text-xs font-medium uppercase tracking-wider text-slate-500 mb-2">{metric.label}</p>
            <div className="flex items-end gap-2">
              <span className="text-2xl font-bold text-white">{metric.value}</span>
              <span className="text-sm text-slate-500 mb-1">/ {metric.max}</span>
            </div>
            <div className="mt-2 h-2 rounded-full bg-slate-800">
              <div
                className={`h-full rounded-full ${
                  metric.color === 'emerald' ? 'bg-emerald-500' : 'bg-amber-500'
                }`}
                style={{ width: `${(metric.value / metric.max) * 100}%` }}
              />
            </div>
          </GlassCard>
        ))}
      </div>

      {/* Risk Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Position Risk</h2>
          <div className="space-y-4">
            {[
              { key: 'risk_per_trade', label: 'Risk Per Trade (%)', min: 0.1, max: 5, step: 0.1 },
              { key: 'max_risk_per_trade', label: 'Max Risk Per Trade (%)', min: 0.5, max: 10, step: 0.1 },
              { key: 'min_risk_reward', label: 'Minimum Risk/Reward', min: 1, max: 5, step: 0.1 },
              { key: 'min_confidence', label: 'Minimum Confidence (%)', min: 50, max: 95, step: 1 },
            ].map((field) => (
              <div key={field.key}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-400">{field.label}</span>
                  <span className="font-semibold text-white">{config[field.key as keyof typeof config]}%</span>
                </div>
                <input
                  type="range"
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  value={config[field.key as keyof typeof config]}
                  onChange={(e) => handleChange(field.key, Number(e.target.value))}
                  className="w-full accent-emerald-500"
                />
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Loss Limits</h2>
          <div className="space-y-4">
            {[
              { key: 'max_daily_loss', label: 'Max Daily Loss (%)', min: 1, max: 20, step: 0.5 },
              { key: 'max_weekly_loss', label: 'Max Weekly Loss (%)', min: 2, max: 30, step: 0.5 },
              { key: 'max_drawdown', label: 'Max Drawdown (%)', min: 5, max: 50, step: 1 },
              { key: 'max_consecutive_losses', label: 'Max Consecutive Losses', min: 2, max: 20, step: 1 },
            ].map((field) => (
              <div key={field.key}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-400">{field.label}</span>
                  <span className="font-semibold text-white">{config[field.key as keyof typeof config]}%</span>
                </div>
                <input
                  type="range"
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  value={config[field.key as keyof typeof config]}
                  onChange={(e) => handleChange(field.key, Number(e.target.value))}
                  className="w-full accent-emerald-500"
                />
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Exposure Limits</h2>
          <div className="space-y-4">
            {[
              { key: 'max_open_positions', label: 'Max Open Positions', min: 1, max: 20, step: 1 },
              { key: 'max_leverage', label: 'Max Leverage (x)', min: 1, max: 10, step: 1 },
              { key: 'max_portfolio_exposure', label: 'Max Portfolio Exposure (%)', min: 10, max: 100, step: 5 },
              { key: 'max_symbol_exposure', label: 'Max Symbol Exposure (%)', min: 5, max: 100, step: 5 },
            ].map((field) => (
              <div key={field.key}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-400">{field.label}</span>
                  <span className="font-semibold text-white">{config[field.key as keyof typeof config]}{field.key.includes('leverage') ? 'x' : field.key.includes('exposure') || field.key.includes('positions') ? '' : ''}</span>
                </div>
                <input
                  type="range"
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  value={config[field.key as keyof typeof config]}
                  onChange={(e) => handleChange(field.key, Number(e.target.value))}
                  className="w-full accent-emerald-500"
                />
              </div>
            ))}
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Risk Rules</h2>
          <div className="space-y-3">
            {[
              { rule: 'Never use Martingale strategy', active: true },
              { rule: 'Never increase position size after a loss', active: true },
              { rule: 'Stop trading after max consecutive losses', active: true },
              { rule: 'Reduce risk by 50% after 3 consecutive losses', active: true },
              { rule: 'Require explicit review after 5 consecutive losses', active: false },
              { rule: 'Block all trades when market data is stale', active: true },
              { rule: 'Block all trades when exchange is disconnected', active: true },
            ].map((item) => (
              <div key={item.rule} className="flex items-center justify-between rounded-lg bg-slate-800/30 px-3 py-2">
                <span className="text-sm text-slate-300">{item.rule}</span>
                <div className={`h-5 w-9 rounded-full p-0.5 cursor-pointer transition-colors ${item.active ? 'bg-emerald-500' : 'bg-slate-700'}`}>
                  <div className={`h-4 w-4 rounded-full bg-white transition-transform ${item.active ? 'translate-x-4' : 'translate-x-0'}`} />
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
