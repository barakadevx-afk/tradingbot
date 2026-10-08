-- Supabase Database Migration for BARAKA AI
-- Run this in the Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'VIEWER',
    is_active BOOLEAN DEFAULT true,
    is_2fa_enabled BOOLEAN DEFAULT false,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Risk configuration table
CREATE TABLE IF NOT EXISTS risk_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    risk_per_trade DECIMAL(5,4) DEFAULT 0.005,
    max_risk_per_trade DECIMAL(5,4) DEFAULT 0.01,
    max_daily_loss DECIMAL(5,4) DEFAULT 0.03,
    max_weekly_loss DECIMAL(5,4) DEFAULT 0.05,
    max_drawdown DECIMAL(5,4) DEFAULT 0.10,
    max_open_positions INTEGER DEFAULT 5,
    max_leverage DECIMAL(5,2) DEFAULT 1.0,
    max_portfolio_exposure DECIMAL(5,4) DEFAULT 0.80,
    max_symbol_exposure DECIMAL(5,4) DEFAULT 0.30,
    max_consecutive_losses INTEGER DEFAULT 5,
    min_confidence DECIMAL(5,2) DEFAULT 0.70,
    min_risk_reward DECIMAL(5,2) DEFAULT 1.5,
    kill_switch_active BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Strategies table
CREATE TABLE IF NOT EXISTS strategies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'inactive',
    markets TEXT[] DEFAULT '{}',
    timeframes TEXT[] DEFAULT '{}',
    ai_model VARCHAR(255),
    performance DECIMAL(10,2) DEFAULT 0,
    risk_profile VARCHAR(50) DEFAULT 'moderate',
    parameters JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- AI Models table
CREATE TABLE IF NOT EXISTS model_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    algorithm VARCHAR(100),
    status VARCHAR(50) DEFAULT 'DRAFT',
    training_period VARCHAR(255),
    validation_accuracy DECIMAL(5,4),
    precision DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    auc DECIMAL(5,4),
    trading_performance DECIMAL(10,2) DEFAULT 0,
    features TEXT[] DEFAULT '{}',
    date_trained TIMESTAMPTZ,
    drift_status VARCHAR(50) DEFAULT 'none',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Signals table
CREATE TABLE IF NOT EXISTS signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    signal_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    symbol VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    timeframe VARCHAR(10),
    signal VARCHAR(10) NOT NULL,
    entry_price DECIMAL(20,8),
    stop_loss DECIMAL(20,8),
    take_profit DECIMAL(20,8),
    risk_reward DECIMAL(5,2),
    confidence DECIMAL(5,2),
    market_regime VARCHAR(50),
    strategy VARCHAR(255),
    model_version VARCHAR(50),
    reasoning_summary TEXT,
    status VARCHAR(50) DEFAULT 'active',
    buy_probability DECIMAL(5,2),
    sell_probability DECIMAL(5,2),
    hold_probability DECIMAL(5,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    client_order_id VARCHAR(255),
    exchange_order_id VARCHAR(255),
    symbol VARCHAR(50) NOT NULL,
    side VARCHAR(10) NOT NULL,
    type VARCHAR(20) NOT NULL,
    quantity DECIMAL(20,8),
    price DECIMAL(20,8),
    filled_quantity DECIMAL(20,8) DEFAULT 0,
    average_fill_price DECIMAL(20,8),
    fees DECIMAL(20,8) DEFAULT 0,
    slippage DECIMAL(20,8) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Positions table
CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    position_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    symbol VARCHAR(50) NOT NULL,
    side VARCHAR(10) NOT NULL,
    quantity DECIMAL(20,8),
    entry_price DECIMAL(20,8),
    current_price DECIMAL(20,8),
    stop_loss DECIMAL(20,8),
    take_profit DECIMAL(20,8),
    unrealized_pnl DECIMAL(20,8) DEFAULT 0,
    unrealized_pnl_percent DECIMAL(10,4) DEFAULT 0,
    leverage DECIMAL(5,2) DEFAULT 1.0,
    strategy VARCHAR(255),
    opened_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ
);

-- Trades table
CREATE TABLE IF NOT EXISTS trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trade_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    symbol VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL,
    entry_price DECIMAL(20,8),
    exit_price DECIMAL(20,8),
    quantity DECIMAL(20,8),
    stop_loss DECIMAL(20,8),
    take_profit DECIMAL(20,8),
    strategy VARCHAR(255),
    ai_model VARCHAR(50),
    signal_confidence DECIMAL(5,2),
    market_regime VARCHAR(50),
    fees DECIMAL(20,8) DEFAULT 0,
    slippage DECIMAL(20,8) DEFAULT 0,
    profit_loss DECIMAL(20,8) DEFAULT 0,
    return_percent DECIMAL(10,4) DEFAULT 0,
    risk_percent DECIMAL(5,4) DEFAULT 0,
    duration VARCHAR(50),
    exit_reason VARCHAR(255),
    opened_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ
);

-- Portfolio snapshots table
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    total_value DECIMAL(20,8),
    cash DECIMAL(20,8),
    open_exposure DECIMAL(20,8),
    realized_pnl DECIMAL(20,8) DEFAULT 0,
    unrealized_pnl DECIMAL(20,8) DEFAULT 0,
    total_pnl DECIMAL(20,8) DEFAULT 0,
    leverage DECIMAL(5,2) DEFAULT 1.0,
    drawdown DECIMAL(5,4) DEFAULT 0,
    daily_pnl DECIMAL(20,8) DEFAULT 0,
    weekly_pnl DECIMAL(20,8) DEFAULT 0,
    monthly_pnl DECIMAL(20,8) DEFAULT 0,
    snapshot_time TIMESTAMPTZ DEFAULT NOW()
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource VARCHAR(255),
    details TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    severity VARCHAR(20) DEFAULT 'info',
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Exchange accounts table
CREATE TABLE IF NOT EXISTS exchange_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    exchange VARCHAR(50) NOT NULL,
    api_key_encrypted TEXT,
    api_secret_encrypted TEXT,
    permissions TEXT[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- System events table
CREATE TABLE IF NOT EXISTS system_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_signals_user_id ON signals(user_id);
CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_positions_user_id ON positions(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_snapshots_user_id ON portfolio_snapshots(user_id);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE trades ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE exchange_accounts ENABLE ROW LEVEL SECURITY;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS 
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
 language 'plpgsql';

-- Add updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_risk_configs_updated_at BEFORE UPDATE ON risk_configs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON strategies FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_model_versions_updated_at BEFORE UPDATE ON model_versions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_exchange_accounts_updated_at BEFORE UPDATE ON exchange_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
