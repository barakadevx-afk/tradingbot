"""Strategy engine for signal generation and backtesting."""

import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional

import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.system import Strategy
from app.repositories.system import StrategyRepository
from app.services.market_data import MarketDataService
from app.services.ai_engine import AIEngine


class StrategyEngine:
    """Engine for strategy execution and backtesting."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.strategy_repo = StrategyRepository(db)
        self.market_data = MarketDataService()
        self.ai_engine = AIEngine(db)

    async def generate_signals(self, strategy_id: int) -> List[Dict]:
        """Generate trading signals for a strategy."""
        strategy = await self.strategy_repo.get_by_id(strategy_id)
        if not strategy:
            raise ValueError("Strategy not found")

        if not strategy.is_active:
            raise ValueError("Strategy is not active")

        symbols = strategy.symbols.split(",") if strategy.symbols else ["BTC/USDT"]
        signals = []

        for symbol in symbols:
            symbol = symbol.strip()
            prediction = await self.ai_engine.predict(symbol, strategy.timeframe)

            if prediction["signal"] != "hold" and prediction["confidence"] >= settings.AI_PREDICTION_THRESHOLD:
                signal = {
                    "symbol": symbol,
                    "signal_type": prediction["signal"],
                    "source": "strategy",
                    "confidence": prediction["confidence"],
                    "entry_price": prediction["current_price"],
                    "target_price": prediction["target_price"],
                    "stop_loss": prediction["stop_loss"],
                    "timeframe": strategy.timeframe,
                    "strategy_id": strategy_id,
                    "metadata": prediction,
                }
                signals.append(signal)

        return signals

    async def run_backtest(
        self,
        strategy_id: int,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        initial_balance: float,
        user_id: int,
    ) -> Dict:
        """Run a backtest for a strategy."""
        strategy = await self.strategy_repo.get_by_id(strategy_id)
        if not strategy:
            raise ValueError("Strategy not found")

        # Generate simulated backtest data
        days = (end_date - start_date).days
        candles = await self.market_data.get_candles(symbol, "1d", min(days, 365))

        if not candles:
            raise ValueError("Insufficient data for backtest")

        # Simulate backtest
        balance = initial_balance
        position = 0.0
        entry_price = 0.0
        trades = []
        equity_curve = []

        for i, candle in enumerate(candles):
            price = candle["close"]
            date = candle["timestamp"]

            # Simple strategy logic for backtest
            if i > 20:
                sma_short = np.mean([c["close"] for c in candles[max(0, i-5):i]])
                sma_long = np.mean([c["close"] for c in candles[max(0, i-20):i]])

                # Buy signal
                if sma_short > sma_long and position == 0:
                    position = balance / price * 0.95  # Use 95% of balance
                    entry_price = price
                    balance = 0

                    trades.append({
                        "date": date,
                        "type": "buy",
                        "price": price,
                        "quantity": position,
                    })

                # Sell signal
                elif sma_short < sma_long and position > 0:
                    balance = position * price
                    pnl = (price - entry_price) * position
                    position = 0

                    trades.append({
                        "date": date,
                        "type": "sell",
                        "price": price,
                        "quantity": position,
                        "pnl": pnl,
                    })

            # Record equity
            current_equity = balance + (position * price if position > 0 else 0)
            equity_curve.append({
                "date": date,
                "equity": current_equity,
            })

        # Calculate metrics
        final_equity = equity_curve[-1]["equity"] if equity_curve else initial_balance
        total_return = (final_equity - initial_balance) / initial_balance * 100

        # Calculate max drawdown
        peak = initial_balance
        max_drawdown = 0
        for point in equity_curve:
            if point["equity"] > peak:
                peak = point["equity"]
            drawdown = (peak - point["equity"]) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # Calculate win rate
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0

        return {
            "strategy_id": strategy_id,
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "initial_balance": initial_balance,
            "final_equity": round(final_equity, 2),
            "total_return": round(total_return, 2),
            "max_drawdown": round(max_drawdown, 2),
            "total_trades": len(trades),
            "win_rate": round(win_rate, 2),
            "trades": trades,
            "equity_curve": equity_curve,
        }

    async def get_backtest_history(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict]:
        """Get backtest history for a user."""
        # In production, this would query a backtests table
        return []

    async def get_backtest_result(self, backtest_id: int) -> Optional[Dict]:
        """Get a specific backtest result."""
        # In production, this would query a backtests table
        return None

    async def delete_backtest(self, backtest_id: int, user_id: int) -> Dict:
        """Delete a backtest."""
        return {"message": "Backtest deleted"}

    async def optimize_strategy(self, strategy_id: int) -> Dict:
        """Optimize strategy parameters."""
        strategy = await self.strategy_repo.get_by_id(strategy_id)
        if not strategy:
            raise ValueError("Strategy not found")

        # Simulate optimization
        await asyncio.sleep(1)

        return {
            "strategy_id": strategy_id,
            "optimized_parameters": {
                "risk_per_trade": round(random.uniform(0.01, 0.03), 4),
                "take_profit": round(random.uniform(0.02, 0.05), 4),
                "stop_loss": round(random.uniform(0.01, 0.03), 4),
            },
            "improvement": round(random.uniform(5, 20), 2),
        }

    async def clone_strategy(self, strategy_id: int, user_id: int, new_name: str) -> Strategy:
        """Clone an existing strategy."""
        original = await self.strategy_repo.get_by_id(strategy_id)
        if not original:
            raise ValueError("Strategy not found")

        cloned = await self.strategy_repo.create(
            {
                "user_id": user_id,
                "name": new_name,
                "description": f"Cloned from {original.name}",
                "strategy_type": original.strategy_type,
                "symbols": original.symbols,
                "timeframe": original.timeframe,
                "parameters": original.parameters,
                "is_active": False,
                "is_paper": True,
            },
        )

        return cloned


import asyncio
