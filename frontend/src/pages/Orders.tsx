import { motion } from 'framer-motion';
import { History, ArrowUpRight, ArrowDownRight, X, Clock } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import StatusBadge from '../components/StatusBadge';
import EmptyState from '../components/EmptyState';
import type { Order } from '../types';

const demoOrders: Order[] = [
  { order_id: 'ord-001', client_order_id: 'cli-001', exchange_order_id: 'ex-001', symbol: 'BTC/USDT', side: 'buy', type: 'market', quantity: 0.029, price: 67432, filled_quantity: 0.029, average_fill_price: 67435, fees: 0.68, slippage: 3, status: 'filled', created_at: new Date(Date.now() - 7200000).toISOString(), updated_at: new Date(Date.now() - 7200000).toISOString() },
  { order_id: 'ord-002', client_order_id: 'cli-002', symbol: 'ETH/USDT', side: 'buy', type: 'limit', quantity: 0.23, price: 3500, filled_quantity: 0.23, average_fill_price: 3498, fees: 0.40, slippage: 2, status: 'filled', created_at: new Date(Date.now() - 14400000).toISOString(), updated_at: new Date(Date.now() - 14400000).toISOString() },
  { order_id: 'ord-003', client_order_id: 'cli-003', symbol: 'SOL/USDT', side: 'sell', type: 'limit', quantity: 5.6, price: 185, filled_quantity: 0, average_fill_price: 0, fees: 0, slippage: 0, status: 'pending', created_at: new Date(Date.now() - 3600000).toISOString(), updated_at: new Date(Date.now() - 3600000).toISOString() },
  { order_id: 'ord-004', client_order_id: 'cli-004', symbol: 'BTC/USDT', side: 'sell', type: 'market', quantity: 0.015, price: 68100, filled_quantity: 0.015, average_fill_price: 68095, fees: 0.51, slippage: 5, status: 'filled', created_at: new Date(Date.now() - 21600000).toISOString(), updated_at: new Date(Date.now() - 21600000).toISOString() },
  { order_id: 'ord-005', client_order_id: 'cli-005', symbol: 'BNB/USDT', side: 'buy', type: 'limit', quantity: 1.2, price: 605, filled_quantity: 0, average_fill_price: 0, fees: 0, slippage: 0, status: 'cancelled', created_at: new Date(Date.now() - 28800000).toISOString(), updated_at: new Date(Date.now() - 25200000).toISOString() },
];

export default function Orders() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Orders</h1>
        <p className="text-sm text-slate-400">Order history and management</p>
      </div>

      {demoOrders.length === 0 ? (
        <EmptyState
          icon={<History className="h-8 w-8" />}
          title="No orders yet"
          description="Orders will appear here when you place trades."
        />
      ) : (
        <GlassCard className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-900/50">
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Symbol</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Side</th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-slate-500">Type</th>
                  <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Quantity</th>
                  <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Price</th>
                  <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Filled</th>
                  <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Fees</th>
                  <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-slate-500">Status</th>
                  <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-slate-500">Time</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {demoOrders.map((order) => (
                  <tr key={order.order_id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3">
                      <span className="text-sm font-semibold text-white">{order.symbol}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className={`flex items-center gap-1 text-sm font-semibold ${
                        order.side === 'buy' ? 'text-emerald-400' : 'text-red-400'
                      }`}>
                        {order.side === 'buy' ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                        {order.side.toUpperCase()}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-slate-300 capitalize">{order.type}</span>
                    </td>
                    <td className="px-4 py-3 text-right text-sm text-slate-300">{order.quantity}</td>
                    <td className="px-4 py-3 text-right text-sm text-slate-300">${order.price.toLocaleString()}</td>
                    <td className="px-4 py-3 text-right text-sm text-slate-300">{order.filled_quantity}</td>
                    <td className="px-4 py-3 text-right text-sm text-slate-300">${order.fees.toFixed(2)}</td>
                    <td className="px-4 py-3 text-center">
                      <StatusBadge status={order.status} size="sm" />
                    </td>
                    <td className="px-4 py-3 text-right text-xs text-slate-500">
                      {new Date(order.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-3">
                      {order.status === 'pending' && (
                        <button className="text-slate-500 hover:text-red-400 transition-colors">
                          <X className="h-4 w-4" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}
    </div>
  );
}
