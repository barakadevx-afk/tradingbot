import { useState } from 'react';
import { motion } from 'framer-motion';
import { Cpu, CheckCircle, XCircle, Eye, GitCompare, AlertTriangle } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import type { AIModel } from '../types';

const demoModels: AIModel[] = [
  { id: 'model-001', name: 'BARAKA Trend Predictor', version: 'v2.1.0', algorithm: 'XGBoost', status: 'PRODUCTION', training_period: '2023-01 to 2024-06', validation_accuracy: 0.72, precision: 0.68, recall: 0.71, f1_score: 0.69, auc: 0.78, trading_performance: 18.2, date_trained: '2024-06-15', drift_status: 'none', features: ['RSI', 'MACD', 'EMA_cross', 'ATR', 'Volume_change', 'BB_position'] },
  { id: 'model-002', name: 'BARAKA Momentum v3', version: 'v3.0.2', algorithm: 'LightGBM', status: 'APPROVED', training_period: '2023-06 to 2024-06', validation_accuracy: 0.69, precision: 0.65, recall: 0.67, f1_score: 0.66, auc: 0.74, trading_performance: 12.5, date_trained: '2024-06-20', drift_status: 'low', features: ['RSI', 'Stochastic', 'ROC', 'EMA_distance', 'Volume'] },
  { id: 'model-003', name: 'BARAKA Range Detector', version: 'v1.2.0', algorithm: 'Random Forest', status: 'TESTING', training_period: '2023-01 to 2024-03', validation_accuracy: 0.65, precision: 0.62, recall: 0.64, f1_score: 0.63, auc: 0.70, trading_performance: 5.8, date_trained: '2024-05-10', drift_status: 'medium', features: ['BB_width', 'ADX', 'Volume', 'Price_position'] },
  { id: 'model-004', name: 'BARAKA Breakout v1', version: 'v1.0.0', algorithm: 'Gradient Boosting', status: 'DRAFT', training_period: '2024-01 to 2024-06', validation_accuracy: 0.58, precision: 0.55, recall: 0.57, f1_score: 0.56, auc: 0.62, trading_performance: 0, date_trained: '2024-06-25', drift_status: 'high', features: ['Volatility', 'Volume_expansion', 'Support_distance'] },
  { id: 'model-005', name: 'BARAKA Legacy v1', version: 'v1.5.0', algorithm: 'Logistic Regression', status: 'RETIRED', training_period: '2022-01 to 2023-06', validation_accuracy: 0.55, precision: 0.52, recall: 0.54, f1_score: 0.53, auc: 0.58, trading_performance: -3.2, date_trained: '2023-06-30', drift_status: 'high', features: ['RSI', 'MACD'] },
];

export default function Models() {
  const [selectedModel, setSelectedModel] = useState<AIModel | null>(null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">AI Models</h1>
        <p className="text-sm text-slate-400">Model registry, performance monitoring, and lifecycle management</p>
      </div>

      {/* Model Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {demoModels.map((model, i) => (
          <motion.div
            key={model.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
          >
            <GlassCard className="p-4" hover>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Cpu className="h-5 w-5 text-cyan-400" />
                  <div>
                    <h3 className="text-sm font-bold text-white">{model.name}</h3>
                    <p className="text-xs text-slate-500">{model.algorithm} • {model.version}</p>
                  </div>
                </div>
                <StatusBadge status={model.status} size="sm" />
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500">Accuracy</span>
                  <span className="font-semibold text-white">{(model.validation_accuracy * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">F1 Score</span>
                  <span className="font-semibold text-white">{model.f1_score.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">AUC</span>
                  <span className="font-semibold text-white">{model.auc.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Trading Perf</span>
                  <span className={`font-semibold ${model.trading_performance >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {model.trading_performance >= 0 ? '+' : ''}{model.trading_performance}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Drift</span>
                  <span className={`font-semibold ${
                    model.drift_status === 'none' ? 'text-emerald-400' :
                    model.drift_status === 'low' ? 'text-amber-400' : 'text-red-400'
                  }`}>
                    {model.drift_status === 'none' ? 'None' : model.drift_status}
                  </span>
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-slate-800/50 flex items-center justify-between">
                <span className="text-[10px] text-slate-500">Trained: {model.date_trained}</span>
                <div className="flex gap-1">
                  <button
                    onClick={() => setSelectedModel(model)}
                    className="rounded p-1 text-slate-500 hover:text-white hover:bg-slate-800 transition-colors"
                    title="View Details"
                  >
                    <Eye className="h-3.5 w-3.5" />
                  </button>
                  {(model.status === 'TESTING' || model.status === 'DRAFT') && (
                    <button className="rounded p-1 text-slate-500 hover:text-emerald-400 hover:bg-slate-800 transition-colors" title="Approve">
                      <CheckCircle className="h-3.5 w-3.5" />
                    </button>
                  )}
                  {model.status !== 'RETIRED' && (
                    <button className="rounded p-1 text-slate-500 hover:text-red-400 hover:bg-slate-800 transition-colors" title="Retire">
                      <XCircle className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
              </div>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* Model Detail Modal */}
      {selectedModel && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl"
          >
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-white">{selectedModel.name}</h2>
                <p className="text-sm text-slate-400">{selectedModel.algorithm} • {selectedModel.version}</p>
              </div>
              <StatusBadge status={selectedModel.status} />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              {[
                { label: 'Accuracy', value: `${(selectedModel.validation_accuracy * 100).toFixed(1)}%` },
                { label: 'Precision', value: selectedModel.precision.toFixed(2) },
                { label: 'Recall', value: selectedModel.recall.toFixed(2) },
                { label: 'F1 Score', value: selectedModel.f1_score.toFixed(2) },
                { label: 'AUC', value: selectedModel.auc.toFixed(2) },
                { label: 'Trading Perf', value: `${selectedModel.trading_performance >= 0 ? '+' : ''}${selectedModel.trading_performance}%` },
                { label: 'Drift Status', value: selectedModel.drift_status },
                { label: 'Date Trained', value: selectedModel.date_trained },
              ].map((item) => (
                <div key={item.label} className="rounded-lg bg-slate-800/50 p-3">
                  <p className="text-[10px] text-slate-500 uppercase tracking-wider">{item.label}</p>
                  <p className="text-sm font-bold text-white mt-0.5">{item.value}</p>
                </div>
              ))}
            </div>

            <div className="mb-6">
              <h3 className="text-sm font-semibold text-white mb-2">Features ({selectedModel.features.length})</h3>
              <div className="flex flex-wrap gap-2">
                {selectedModel.features.map((f) => (
                  <span key={f} className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                    {f}
                  </span>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setSelectedModel(null)}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 transition-colors"
              >
                Close
              </button>
              {selectedModel.status === 'TESTING' && (
                <button className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-400 transition-colors">
                  Approve Model
                </button>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}
