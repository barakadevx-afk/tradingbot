// BARAKA AI - Type Definitions

export type TradingMode = 'paper' | 'live' | 'backtest';
export type SignalType = 'BUY' | 'SELL' | 'HOLD';
export type OrderStatus = 'pending' | 'open' | 'filled' | 'partially_filled' | 'cancelled' | 'rejected' | 'expired';
export type OrderType = 'market' | 'limit' | 'stop' | 'stop_limit';
export type PositionSide = 'long' | 'short';
export type ModelStatus = 'DRAFT' | 'TESTING' | 'APPROVED' | 'PRODUCTION' | 'RETIRED';
export type MarketRegime = 'TREND_UP' | 'TREND_DOWN' | 'RANGE' | 'BREAKOUT' | 'BREAKDOWN' | 'HIGH_VOLATILITY' | 'LOW_VOLATILITY' | 'UNCERTAIN';
export type SystemStatus = 'HEALTHY' | 'WARNING' | 'CRITICAL' | 'OFFLINE';
export type UserRole = 'SUPER_ADMIN' | 'ADMIN' | 'TRADER' | 'ANALYST' | 'VIEWER';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_2fa_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface Market {
  symbol: string;
  base: string;
  quote: string;
  price: number;
  change_24h: number;
  volume_24h: number;
  high_24h: number;
  low_24h: number;
  bid: number;
  ask: number;
  spread: number;
  spread_percent: number;
  liquidity_score: number;
  volatility: number;
  is_enabled: boolean;
}

export interface Candle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Signal {
  signal_id: string;
  symbol: string;
  timestamp: string;
  timeframe: string;
  signal: SignalType;
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  risk_reward: number;
  confidence: number;
  market_regime: MarketRegime;
  strategy: string;
  model_version: string;
  reasoning_summary: string;
  status: 'active' | 'executed' | 'expired' | 'cancelled';
  buy_probability: number;
  sell_probability: number;
  hold_probability: number;
}

export interface Order {
  order_id: string;
  client_order_id: string;
  exchange_order_id?: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: OrderType;
  quantity: number;
  price: number;
  filled_quantity: number;
  average_fill_price: number;
  fees: number;
  slippage: number;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
}

export interface Position {
  position_id: string;
  symbol: string;
  side: PositionSide;
  quantity: number;
  entry_price: number;
  current_price: number;
  stop_loss: number;
  take_profit: number;
  unrealized_pnl: number;
  unrealized_pnl_percent: number;
  leverage: number;
  opened_at: string;
  strategy: string;
}

export interface Trade {
  trade_id: string;
  symbol: string;
  direction: PositionSide;
  entry_price: number;
  exit_price: number;
  quantity: number;
  stop_loss: number;
  take_profit: number;
  strategy: string;
  ai_model: string;
  signal_confidence: number;
  market_regime: MarketRegime;
  fees: number;
  slippage: number;
  profit_loss: number;
  return_percent: number;
  risk_percent: number;
  duration: string;
  exit_reason: string;
  opened_at: string;
  closed_at: string;
}

export interface Portfolio {
  total_value: number;
  cash: number;
  open_exposure: number;
  realized_pnl: number;
  unrealized_pnl: number;
  total_pnl: number;
  leverage: number;
  drawdown: number;
  daily_pnl: number;
  weekly_pnl: number;
  monthly_pnl: number;
  equity_curve: EquityPoint[];
  allocation: Allocation[];
}

export interface EquityPoint {
  timestamp: string;
  value: number;
}

export interface Allocation {
  symbol: string;
  value: number;
  percentage: number;
}

export interface RiskConfig {
  risk_per_trade: number;
  max_risk_per_trade: number;
  max_daily_loss: number;
  max_weekly_loss: number;
  max_drawdown: number;
  max_open_positions: number;
  max_leverage: number;
  max_portfolio_exposure: number;
  max_symbol_exposure: number;
  max_consecutive_losses: number;
  min_confidence: number;
  min_risk_reward: number;
  kill_switch_active: boolean;
  daily_loss_used: number;
  drawdown_used: number;
  exposure_used: number;
  current_risk_level: 'low' | 'medium' | 'high' | 'critical';
}

export interface Strategy {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'backtesting';
  markets: string[];
  timeframes: string[];
  ai_model: string;
  performance: number;
  risk_profile: 'conservative' | 'moderate' | 'aggressive';
  created_at: string;
  parameters: Record<string, number>;
}

export interface AIModel {
  id: string;
  name: string;
  version: string;
  algorithm: string;
  status: ModelStatus;
  training_period: string;
  validation_accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  auc: number;
  trading_performance: number;
  date_trained: string;
  drift_status: 'none' | 'low' | 'medium' | 'high';
  features: string[];
}

export interface Alert {
  id: string;
  type: 'trade_opened' | 'trade_closed' | 'stop_loss' | 'take_profit' | 'signal' | 'drawdown' | 'daily_loss' | 'exchange' | 'system' | 'kill_switch' | 'model';
  title: string;
  message: string;
  severity: 'info' | 'warning' | 'critical';
  read: boolean;
  created_at: string;
}

export interface SystemHealth {
  service: string;
  status: SystemStatus;
  latency_ms: number;
  last_heartbeat: string;
  cpu_percent: number;
  memory_percent: number;
}

export interface AuditLog {
  id: string;
  user_id: string;
  action: string;
  resource: string;
  details: string;
  ip_address: string;
  created_at: string;
}

export interface BacktestResult {
  id: string;
  symbol: string;
  strategy: string;
  timeframe: string;
  start_date: string;
  end_date: string;
  starting_balance: number;
  ending_balance: number;
  total_return: number;
  net_profit: number;
  annualized_return: number;
  win_rate: number;
  loss_rate: number;
  profit_factor: number;
  expectancy: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  calmar_ratio: number;
  max_drawdown: number;
  avg_win: number;
  avg_loss: number;
  largest_win: number;
  largest_loss: number;
  avg_holding_time: string;
  total_trades: number;
  long_trades: number;
  short_trades: number;
  equity_curve: EquityPoint[];
  drawdown_curve: EquityPoint[];
  monthly_returns: MonthlyReturn[];
  trades: Trade[];
}

export interface MonthlyReturn {
  month: string;
  return: number;
}

export interface Performance {
  total_return: number;
  net_profit: number;
  win_rate: number;
  profit_factor: number;
  sharpe_ratio: number;
  max_drawdown: number;
  best_strategy: string;
  worst_strategy: string;
  best_asset: string;
  worst_asset: string;
  by_weekday: Record<string, number>;
  by_hour: Record<string, number>;
  by_regime: Record<string, number>;
  by_strategy: Record<string, number>;
}
