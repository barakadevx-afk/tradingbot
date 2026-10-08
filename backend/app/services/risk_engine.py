"""Risk engine for trade validation, position sizing, and drawdown checks."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.trading import Order, Position, Trade
from app.models.system import RiskConfig
from app.repositories.system import RiskConfigRepository


class RiskEngine:
    """Engine for risk management and validation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.risk_repo = RiskConfigRepository(db)

    async def validate_trade(
        self,
        user_id: int,
        symbol: str,
        quantity: float,
        price: float,
        side: str,
    ) -> Dict:
        """Validate a trade against risk parameters."""
        config = await self.risk_repo.get_by_user_id(user_id)
        if not config:
            return {"valid": False, "reason": "Risk config not found"}

        # Check kill switch
        if config.kill_switch_active or settings.KILL_SWITCH_ENABLED:
            return {"valid": False, "reason": "Kill switch is active"}

        trade_value = quantity * price

        # Check position size
        max_position_value = await self._get_max_position_value(user_id, config)
        if trade_value > max_position_value:
            return {
                "valid": False,
                "reason": f"Position size {trade_value} exceeds max {max_position_value}",
            }

        # Check daily loss limit
        daily_pnl = await self._get_daily_pnl(user_id)
        if daily_pnl < 0 and abs(daily_pnl) >= config.daily_loss_limit:
            return {"valid": False, "reason": "Daily loss limit reached"}

        # Check max open positions
        open_positions = await self._get_open_positions_count(user_id)
        if open_positions >= config.max_open_positions:
            return {
                "valid": False,
                "reason": f"Max open positions ({config.max_open_positions}) reached",
            }

        # Check max trades per day
        daily_trades = await self._get_daily_trade_count(user_id)
        if daily_trades >= config.max_trades_per_day:
            return {
                "valid": False,
                "reason": f"Max trades per day ({config.max_trades_per_day}) reached",
            }

        # Calculate position size based on risk
        position_size = self.calculate_position_size(
            balance=await self._get_portfolio_value(user_id),
            risk_per_trade=config.risk_per_trade,
            entry_price=price,
            stop_loss=price * 0.98 if side == "buy" else price * 1.02,
        )

        return {
            "valid": True,
            "position_size": round(position_size, 8),
            "risk_amount": round(trade_value * config.risk_per_trade, 2),
            "max_loss": round(position_size * price * config.risk_per_trade, 2),
        }

    def calculate_position_size(
        self,
        balance: float,
        risk_per_trade: float,
        entry_price: float,
        stop_loss: float,
    ) -> float:
        """Calculate optimal position size based on risk parameters."""
        risk_amount = balance * risk_per_trade
        price_risk = abs(entry_price - stop_loss)

        if price_risk == 0:
            return 0

        position_size = risk_amount / price_risk
        return position_size

    async def get_risk_status(self, user_id: int) -> Dict:
        """Get current risk status and metrics."""
        config = await self.risk_repo.get_by_user_id(user_id)
        if not config:
            return {"error": "Risk config not found"}

        daily_pnl = await self._get_daily_pnl(user_id)
        daily_trades = await self._get_daily_trade_count(user_id)
        open_positions = await self._get_open_positions_count(user_id)
        portfolio_value = await self._get_portfolio_value(user_id)

        return {
            "kill_switch_active": config.kill_switch_active,
            "daily_pnl": round(daily_pnl, 2),
            "daily_loss_limit": config.daily_loss_limit,
            "daily_loss_remaining": round(config.daily_loss_limit - abs(min(daily_pnl, 0)), 2),
            "daily_trades": daily_trades,
            "max_trades_per_day": config.max_trades_per_day,
            "open_positions": open_positions,
            "max_open_positions": config.max_open_positions,
            "portfolio_value": round(portfolio_value, 2),
            "risk_per_trade": config.risk_per_trade,
            "max_position_size": config.max_position_size,
            "max_leverage": config.max_leverage,
        }

    async def get_exposure(self, user_id: int) -> Dict:
        """Get current risk exposure."""
        result = await self.db.execute(
            select(func.sum(Position.quantity * Position.entry_price)).where(
                Position.user_id == user_id,
                Position.is_open == True,
            )
        )
        total_exposure = result.scalar() or 0

        portfolio_value = await self._get_portfolio_value(user_id)

        exposure_pct = (total_exposure / portfolio_value * 100) if portfolio_value > 0 else 0

        return {
            "total_exposure": round(total_exposure, 2),
            "portfolio_value": round(portfolio_value, 2),
            "exposure_percentage": round(exposure_pct, 2),
            "positions_by_symbol": await self._get_exposure_by_symbol(user_id),
        }

    async def emergency_close_all(self, user_id: int) -> Dict:
        """Emergency close all positions."""
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.is_open == True,
            )
        )
        positions = result.scalars().all()

        closed_count = 0
        for position in positions:
            position.is_open = False
            position.closed_at = datetime.now(timezone.utc)
            closed_count += 1

        await self.db.commit()

        return {
            "closed_positions": closed_count,
            "message": f"Emergency closed {closed_count} positions",
        }

    async def _get_max_position_value(self, user_id: int, config: RiskConfig) -> float:
        """Get maximum position value based on risk config."""
        portfolio_value = await self._get_portfolio_value(user_id)
        return portfolio_value * config.max_position_size

    async def _get_daily_pnl(self, user_id: int) -> float:
        """Get today's P&L."""
        today = datetime.now(timezone.utc).date()
        result = await self.db.execute(
            select(func.sum(Trade.pnl)).where(
                Trade.user_id == user_id,
                func.date(Trade.executed_at) == today,
            )
        )
        return result.scalar() or 0

    async def _get_daily_trade_count(self, user_id: int) -> int:
        """Get today's trade count."""
        today = datetime.now(timezone.utc).date()
        result = await self.db.execute(
            select(func.count(Trade.id)).where(
                Trade.user_id == user_id,
                func.date(Trade.executed_at) == today,
            )
        )
        return result.scalar() or 0

    async def _get_open_positions_count(self, user_id: int) -> int:
        """Get count of open positions."""
        result = await self.db.execute(
            select(func.count(Position.id)).where(
                Position.user_id == user_id,
                Position.is_open == True,
            )
        )
        return result.scalar() or 0

    async def _get_portfolio_value(self, user_id: int) -> float:
        """Get total portfolio value."""
        # Simplified - in production, this would calculate from actual balances
        return settings.PAPER_TRADING_DEFAULT_BALANCE

    async def _get_exposure_by_symbol(self, user_id: int) -> Dict[str, float]:
        """Get exposure breakdown by symbol."""
        result = await self.db.execute(
            select(
                Position.symbol,
                func.sum(Position.quantity * Position.entry_price),
            ).where(
                Position.user_id == user_id,
                Position.is_open == True,
            ).group_by(Position.symbol)
        )
        return {symbol: round(value, 2) for symbol, value in result.all()}
