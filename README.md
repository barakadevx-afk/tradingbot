# BARAKA AI

**Trade Smarter. Grow Faster.**

Intelligent Crypto Trading Platform

BARAKA AI is a professional-grade full-stack crypto trading and market-analysis platform that combines real-time market data, technical analysis, quantitative trading strategies, AI/ML models, risk management, backtesting, paper trading, portfolio management, analytics, alerts, and optional live exchange execution.

**BARAKA AI prioritizes capital protection over forcing trades. When there is no high-quality opportunity: HOLD.**

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Docker Setup](#docker-setup)
- [Frontend Setup](#frontend-setup)
- [Backend Setup](#backend-setup)
- [Running Tests](#running-tests)
- [Paper Trading](#paper-trading)
- [Exchange Testnet Connection](#exchange-testnet-connection)
- [Production Deployment](#production-deployment)
- [Security Guidelines](#security-guidelines)
- [Live Trading Safety Checklist](#live-trading-safety-checklist)
- [API Documentation](#api-documentation)
- [WebSocket Events](#websocket-events)
- [Monitoring](#monitoring)
- [CI/CD](#cicd)
- [License](#license)

---

## Features

### Trading Modes
- **BACKTEST** — Historical data only, no real orders
- **PAPER** — Default mode, simulated funds (,000 virtual balance)
- **LIVE** — Locked by default, requires explicit safety validation

### Core Engines
- **Market Data Engine** — REST + WebSocket, OHLCV, order book, data validation
- **Technical Analysis** — EMA, SMA, ADX, RSI, MACD, Stochastic, ATR, Bollinger Bands
- **Market Regime Detection** — TREND_UP, TREND_DOWN, RANGE, BREAKOUT, BREAKDOWN, etc.
- **AI/ML Engine** — Logistic Regression, Random Forest, XGBoost, LightGBM with walk-forward validation
- **Strategy Engine** — Trend Following, Breakout, Pullback, Mean Reversion
- **Risk Engine** — Position sizing, drawdown protection, kill switch, consecutive loss protection
- **Execution Engine** — Paper trading with realistic fees, slippage, order lifecycle
- **Backtesting Engine** — Equity curve, drawdown, Monte Carlo, walk-forward validation

### Supported Markets
BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT, XRP/USDT, ADA/USDT, DOGE/USDT

### Multi-Timeframe Analysis
1D (macro) → 4H (trend) → 1H (setup) → 15M (entry) → 5M (execution)

---

## Architecture

`
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│  Dashboard │ Trading │ Signals │ Portfolio │ Backtesting     │
│  Risk │ Models │ Strategies │ Scanner │ Analytics           │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API / WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│                     BACKEND (FastAPI)                        │
│  Auth │ Markets │ Signals │ Portfolio │ Risk │ Strategies   │
│  Models │ Backtests │ Paper │ Kill Switch │ System          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   TRADING ENGINE (Python)                    │
│  Market Data │ Indicators │ Regimes │ Strategies │ Signals   │
│  Risk │ Execution │ Portfolio                                 │
├──────────────────────────────────────────────────────────────┤
│                    ML ENGINE (Python)                        │
│  Features │ Training │ Inference │ Registry │ Monitoring     │
├──────────────────────────────────────────────────────────────┤
│                 BACKTESTING ENGINE (Python)                  │
│  Engine │ Metrics │ Walk-Forward │ Monte Carlo              │
└──────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              PostgreSQL │ Redis │ Exchange APIs              │
└─────────────────────────────────────────────────────────────┘
`

---

## Project Structure

`
baraka-ai/
├── frontend/                    # React + TypeScript + Vite + Tailwind
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # 26 page components
│   │   ├── layouts/             # App layout with sidebar
│   │   ├── hooks/               # Custom React hooks
│   │   ├── services/            # API client services
│   │   ├── store/               # Zustand state management
│   │   ├── types/               # TypeScript type definitions
│   │   └── utils/               # Utility functions
│   ├── Dockerfile
│   └── nginx.conf
├── backend/                     # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/v1/              # 14 API routers
│   │   ├── core/                # Config, security, dependencies
│   │   ├── db/                  # Database base and session
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic services
│   │   ├── repositories/        # Data access layer
│   │   └── auth/                # JWT + RBAC
│   ├── Dockerfile
│   └── requirements.txt
├── trading-engine/              # Core trading logic
│   ├── market_data/             # OHLCV feed, order book
│   ├── indicators/              # Technical indicators
│   ├── regimes/                 # Market regime detection
│   ├── strategies/              # Trading strategies
│   ├── signals/                 # Signal generation
│   ├── risk/                    # Risk engine, position sizing
│   ├── execution/               # Paper executor, order manager
│   └── portfolio/               # Portfolio tracking
├── ml-engine/                   # Machine learning pipeline
│   ├── features/                # Feature engineering
│   ├── training/                # Model training + walk-forward
│   ├── inference/               # Prediction service
│   ├── registry/                # Model lifecycle management
│   └── monitoring/              # Drift detection
├── backtesting/                 # Backtesting engine
│   ├── engine.py                # Core backtester
│   ├── metrics.py               # Performance metrics
│   ├── walk_forward.py          # Walk-forward validation
│   ├── monte_carlo.py           # Monte Carlo simulation
│   └── data_loader.py           # Historical data loading
├── infrastructure/              # Nginx config, SSL
├── tests/                       # Automated tests
├── docs/                        # Documentation
├── docker-compose.yml           # Full stack orchestration
├── .env.example                 # Environment template
└── README.md                    # This file
`

---

## Installation

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

### Quick Start (Docker)
`ash
# Clone and navigate
cd baraka-ai

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
`

---

## Environment Variables

Copy .env.example to .env and configure:

`env
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=change-me-in-production

# Database
DATABASE_URL=postgresql+asyncpg://baraka:baraka_secret@localhost:5432/baraka_ai

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=change-me-to-secure-random-string-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Trading
TRADING_MODE=paper
DEFAULT_PAPER_BALANCE=10000
RISK_PER_TRADE=0.005
MAX_DAILY_LOSS=0.03
MAX_DRAWDOWN=0.10

# Exchange (NEVER commit real keys)
BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_TESTNET=true
`

---

## Database Setup

`ash
# Create database
createdb baraka_ai

# Run migrations
cd backend
alembic upgrade head

# Or let SQLAlchemy create tables (development only)
# Tables are auto-created on first startup
`

---

## Docker Setup

`ash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Reset volumes (WARNING: deletes all data)
docker-compose down -v
`

Services:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Nginx: http://localhost:80

---

## Frontend Setup

`ash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
`

---

## Backend Setup

`ash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/ -v
`

---

## Running Tests

`ash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm run test

# All tests (Docker)
docker-compose run backend pytest tests/ -v
`

---

## Paper Trading

Paper trading is the **default mode**. No real money is required.

1. Register an account
2. Navigate to Dashboard
3. Confirm PAPER MODE badge is displayed
4. Explore AI Signals
5. Run a backtest
6. Start paper trading from the Trading page

Paper engine simulates:
- Orders and fills
- Trading fees (0.1%)
- Slippage (0.05%)
- Position tracking
- Portfolio equity
- Drawdown monitoring

---

## Exchange Testnet Connection

1. Create testnet API keys:
   - Binance: https://testnet.binancefuture.com
   - Bybit: https://testnet.bybit.com

2. Navigate to Exchange Connections page

3. Add exchange with testnet keys

4. Verify connection status

5. **Never use mainnet keys in development**

---

## Production Deployment

### Pre-deployment Checklist
- [ ] All tests passing
- [ ] Security audit completed
- [ ] Database backups configured
- [ ] Monitoring and alerting active
- [ ] SSL certificates installed
- [ ] Rate limiting configured
- [ ] CORS restricted to production domain
- [ ] Secrets moved to secret manager
- [ ] Kill switch tested
- [ ] Paper trading validated for minimum 30 days

### Deployment Steps
1. Set ENVIRONMENT=production
2. Set DEBUG=false
3. Configure production database
4. Set strong JWT_SECRET_KEY and SECRET_KEY
5. Build Docker images
6. Deploy with docker-compose or Kubernetes
7. Configure reverse proxy (nginx)
8. Enable HTTPS
9. Set up monitoring (Prometheus + Grafana)

---

## Security Guidelines

### Never
- Hard-code API keys or secrets
- Send exchange secrets to frontend
- Commit .env to version control
- Use mainnet keys in development
- Enable LIVE trading without full validation
- Grant withdrawal permissions to exchange API keys

### Always
- Encrypt exchange credentials at rest
- Use JWT with short expiry + refresh tokens
- Implement rate logging
- Log all security-relevant actions
- Validate all user inputs
- Use HTTPS in production
- Rotate API keys regularly
- Monitor for unusual activity

---

## Live Trading Safety Checklist

Before enabling LIVE trading, verify:

- [ ] Exchange API connection stable
- [ ] API trading permission enabled
- [ ] API key valid and not expired
- [ ] Market data feed healthy
- [ ] Risk engine functioning
- [ ] Maximum daily loss configured
- [ ] Maximum drawdown configured
- [ ] Approved strategy active
- [ ] Approved AI model active
- [ ] Kill switch functioning
- [ ] Database connection healthy
- [ ] System monitoring active
- [ ] Audit logging enabled
- [ ] Paper trading validated for 30+ days
- [ ] Testnet trading validated
- [ ] Emergency contacts configured

**If any check fails: LIVE TRADING DISABLED**

---

## API Documentation

Interactive API docs available at /docs (Swagger UI) when backend is running.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/register | Create account |
| POST | /api/v1/auth/login | Login |
| POST | /api/v1/auth/refresh | Refresh token |
| GET | /api/v1/markets | List markets |
| GET | /api/v1/signals | Get signals |
| GET | /api/v1/portfolio | Portfolio overview |
| GET | /api/v1/risk | Risk configuration |
| PUT | /api/v1/risk | Update risk config |
| GET | /api/v1/strategies | List strategies |
| GET | /api/v1/models | AI models |
| POST | /api/v1/backtests | Create backtest |
| POST | /api/v1/paper/start | Start paper trading |
| POST | /api/v1/kill-switch | Activate kill switch |
| GET | /api/v1/system/health | System health |
| GET | /api/v1/audit-logs | Audit logs |

---

## WebSocket Events

Connect to /ws/{channel} for real-time updates:

| Channel | Events |
|---------|--------|
| /ws/market | prices, candles, order book |
| /ws/trading | signals, positions, orders |
| /ws/system | health, alerts, risk |

---

## Monitoring

### Metrics Tracked
- API latency
- Market data latency
- Order errors
- Exchange reconnects
- Risk violations
- AI inference latency
- CPU and memory usage
- Database health

### Integration
- Prometheus metrics endpoint: /metrics
- Grafana dashboards: import from infrastructure/grafana/
- Structured JSON logging

---

## CI/CD

GitHub Actions workflow (.github/workflows/ci.yml):

1. Lint (flake8, black, ruff)
2. Type check (mypy)
3. Tests (pytest, jest)
4. Build (Docker images)
5. Security scan (bandit, safety)
6. Deploy (manual approval required)

**Never automatically deploy live-trading strategy changes without review.**

---

## License

MIT License

---

## Disclaimer

BARAKA AI does not guarantee profit. Trading cryptocurrency involves substantial risk of loss.
Past performance does not guarantee future results. Always do your own research and never
invest more than you can afford to lose.

**BARAKA AI should prefer protecting capital over forcing trades.**
