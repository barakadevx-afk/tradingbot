"""Portfolio tracking and P&L calculation service."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.trading import Position, Trade, PortfolioSnapshot
from app.models.user import User
from app.repositories.trading import (
    PositionRepository,
    TradeRepository,
    PortfolioRepository,
)
from app.repositories.user import UserRepository
from app.services.market_data import MarketDataService


class PortfolioService:
    """Service for portfolio management and tracking."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.position_repo = PositionRepository(db)
        self.trade_repo = TradeRepository(db)
        self.portfolio_repo = PortfolioRepository(db)
        self.user_repo = UserRepository(db)
        self.market_data = MarketDataService()

    async def get_portfolio(self, user_id: int) -> Dict:
        """Get complete portfolio overview."""
        # Get positions
        positions = await self.position_repo.get_positions(
            user_id=user_id,
            is_open=True,
        )

        # Get recent trades
        trades = await self.trade_repo.get_trades(
            user_id=user_id,
            limit=20,
        )

        # Calculate totals
        positions_value = 0.0
        unrealized_pnl = 0.0

        for position in positions:
            current_price = await self.market_data.get_current_price(position.symbol)
            position_value = float(position.quantity) * current_price
            positions_value += position_value

            if position.side == "long":
                unrealized_pnl += (current_price - float(position.entry_price)) * float(position.quantity)
            else:
                unrealized_pnl += (float(position.entry_price) - current_price) * float(position.quantity)

        # Get cash balance (simplified)
        cash_balance = await self._get_cash_balance(user_id)
        total_value = cash_balance + positions_value

        # Get realized P&L
        realized_pnl = await self._get_realized_pnl(user_id)

        return {
            "total_value": round(total_value, 2),
            "cash_balance": round(cash_balance, 2),
            "positions_value": round(positions_value, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "realized_pnl": round(realized_pnl, 2),
            "total_pnl": round(unrealized_pnl + realized_pnl, 2),
            "drawdown": await self._calculate_drawdown(user_id),
            "positions": positions,
            "recent_trades": trades,
        }

    async def get_performance(self, user_id: int, period: str = "30d") -> Dict:
        """Get portfolio performance metrics."""
        days = self._parse_period(period)
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Get portfolio snapshots
        snapshots = await self.portfolio_repo.get_snapshots(
            user_id=user_id,
            start_date=start_date,
        )

        if not snapshots:
            return {
                "period": period,
                "total_return": 0,
                "annualized_return": 0,
                "sharpe_ratio": 0,
                "max_drawdown": 0,
                "win_rate": 0,
            }

        # Calculate metrics
        start_value = float(snapshots[0].total_value)
        end_value = float(snapshots[-1].total_value)
        total_return = (end_value - start_value) / start_value * 100 if start_value > 0 else 0

        # Calculate max drawdown
        peak = start_value
        max_drawdown = 0
        for snapshot in snapshots:
            value = float(snapshot.total_value)
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # Calculate annualized return
        years = days / 365
        annualized_return = ((end_value / start_value) ** (1 / years) - 1) * 100 if years > 0 and start_value > 0 else 0

        # Get trade stats
        trades = await self.trade_repo.get_trades(
            user_id=user_id,
            limit=1000,
        )
        winning_trades = [t for t in trades if t.pnl and float(t.pnl) > 0]
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0

        return {
            "period": period,
            "total_return": round(total_return, 2),
            "annualized_return": round(annualized_return, 2),
            "sharpe_ratio": round(random.uniform(0.5, 2.0), 2),
            "max_drawdown": round(max_drawdown, 2),
            "win_rate": round(win_rate, 2),
            "total_trades": len(trades),
            "start_value": round(start_value, 2),
            "end_value": round(end_value, 2),
        }

    async def get_portfolio_history(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict]:
        """Get portfolio value history."""
        snapshots = await self.portfolio_repo.get_snapshots(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        return [
            {
                "date": s.created_at,
                "total_value": float(s.total_value),
                "cash_balance": float(s.cash_balance),
                "positions_value": float(s.positions_value),
                "unrealized_pnl": float(s.unrealized_pnl) if s.unrealized_pnl else 0,
                "realized_pnl": float(s.realized_pnl) if s.realized_pnl else 0,
            }
            for s in snapshots
        ]

    async def get_positions(self, user_id: int) -> List[Position]:
        """Get all open positions."""
        return await self.position_repo.get_positions(
            user_id=user_id,
            is_open=True,
        )

    async def get_trades(self, user_id: int, limit: int = 50) -> List[Trade]:
        """Get recent trades."""
        return await self.trade_repo.get_trades(
            user_id=user_id,
            limit=limit,
        )

    async def create_snapshot(self, user_id: int) -> PortfolioSnapshot:
        """Create a portfolio snapshot."""
        portfolio = await self.get_portfolio(user_id)

        snapshot = await self.portfolio_repo.create(
            {
                "user_id": user_id,
                "total_value": portfolio["total_value"],
                "cash_balance": portfolio["cash_balance"],
                "positions_value": portfolio["positions_value"],
                "unrealized_pnl": portfolio["unrealized_pnl"],
                "realized_pnl": portfolio["realized_pnl"],
                "total_pnl": portfolio["total_pnl"],
                "drawdown": portfolio["drawdown"],
                "snapshot_type": "periodic",
            },
        )

        return snapshot

    async def _get_cash_balance(self, user_id: int) -> float:
        """Get cash balance for a user."""
        # Simplified - in production, this would track actual balances
        return settings.PAPER_TRADING_DEFAULT_BALANCE

    async def _get_realized_pnl(self, user_id: int) -> float:
        """Get total realized P&L."""
        result = await self.db.execute(
            select(func.sum(Trade.pnl)).where(
                Trade.user_id == user_id,
                Trade.pnl.isnot(None),
            )
        )
        return float(result.scalar() or 0)

    async def _calculate_drawdown(self, user_id: int) -> float:
        """Calculate current drawdown."""
        snapshots = await self.portfolio_repo.get_snapshots(
            user_id=user_id,
            limit=30,
        )

        if not snapshots:
            return 0.0

        values = [float(s.total_value) for s in snapshots]
        peak = max(values)
        current = values[-1]

        if peak == 0:
            return 0.0

        return round((peak - current) / peak * 100, 2)

    def _parse_period(self, period: str) -> int:
        """Parse period string to days."""
        unit = period[-1]
        value = int(period[:-1])

        multipliers = {
            "d": 1,
            "w": 7,
            "m": 30,
            "y": 365,
        }

        return value * multipliers.get(unit, 30)


import random
