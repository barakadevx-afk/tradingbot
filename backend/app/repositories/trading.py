"""Trading data repositories."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trading import Signal, Order, Position, Trade, PortfolioSnapshot
from app.repositories.base import BaseRepository


class SignalRepository(BaseRepository[Signal]):
    """Repository for trading signals."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Signal)

    async def get_signals(
        self,
        symbol: Optional[str] = None,
        signal_type: Optional[str] = None,
        source: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Signal]:
        """Get signals with filters."""
        query = select(Signal)

        if symbol:
            query = query.where(Signal.symbol == symbol)
        if signal_type:
            query = query.where(Signal.signal_type == signal_type)
        if source:
            query = query.where(Signal.source == source)
        if is_active is not None:
            query = query.where(Signal.is_active == is_active)

        query = query.order_by(Signal.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_signals(self, symbol: Optional[str] = None) -> List[Signal]:
        """Get active signals."""
        query = select(Signal).where(Signal.is_active == True)

        if symbol:
            query = query.where(Signal.symbol == symbol)

        result = await self.db.execute(query)
        return list(result.scalars().all())


class OrderRepository(BaseRepository[Order]):
    """Repository for orders."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Order)

    async def get_orders(
        self,
        user_id: int,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        side: Optional[str] = None,
        is_paper: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Order]:
        """Get orders with filters."""
        query = select(Order).where(Order.user_id == user_id)

        if symbol:
            query = query.where(Order.symbol == symbol)
        if status:
            query = query.where(Order.status == status)
        if side:
            query = query.where(Order.side == side)
        if is_paper is not None:
            query = query.where(Order.is_paper == is_paper)

        query = query.order_by(Order.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_open_orders(self, user_id: int) -> List[Order]:
        """Get open orders for a user."""
        result = await self.db.execute(
            select(Order).where(
                Order.user_id == user_id,
                Order.status.in_(["pending", "open"]),
            )
        )
        return list(result.scalars().all())

    async def get_orders_by_status(self, status: str) -> List[Order]:
        """Get orders by status."""
        result = await self.db.execute(
            select(Order).where(Order.status == status)
        )
        return list(result.scalars().all())


class PositionRepository(BaseRepository[Position]):
    """Repository for positions."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Position)

    async def get_positions(
        self,
        user_id: int,
        symbol: Optional[str] = None,
        is_open: Optional[bool] = None,
        side: Optional[str] = None,
    ) -> List[Position]:
        """Get positions with filters."""
        query = select(Position).where(Position.user_id == user_id)

        if symbol:
            query = query.where(Position.symbol == symbol)
        if is_open is not None:
            query = query.where(Position.is_open == is_open)
        if side:
            query = query.where(Position.side == side)

        query = query.order_by(Position.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_open_positions(self, user_id: int) -> List[Position]:
        """Get open positions for a user."""
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.is_open == True,
            )
        )
        return list(result.scalars().all())

    async def get_position_by_symbol(
        self, user_id: int, symbol: str
    ) -> Optional[Position]:
        """Get open position by symbol."""
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.symbol == symbol,
                Position.is_open == True,
            )
        )
        return result.scalar_one_or_none()


class TradeRepository(BaseRepository[Trade]):
    """Repository for trades."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Trade)

    async def get_trades(
        self,
        user_id: int,
        symbol: Optional[str] = None,
        side: Optional[str] = None,
        is_paper: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Trade]:
        """Get trades with filters."""
        query = select(Trade).where(Trade.user_id == user_id)

        if symbol:
            query = query.where(Trade.symbol == symbol)
        if side:
            query = query.where(Trade.side == side)
        if is_paper is not None:
            query = query.where(Trade.is_paper == is_paper)

        query = query.order_by(Trade.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_trade_stats(self, user_id: int, period: str = "30d") -> dict:
        """Get trade statistics."""
        days = self._parse_period(period)
        start_date = datetime.now(timezone.utc) - __import__("datetime").timedelta(days=days)

        result = await self.db.execute(
            select(
                func.count(Trade.id),
                func.sum(Trade.pnl),
                func.avg(Trade.pnl),
            ).where(
                Trade.user_id == user_id,
                Trade.executed_at >= start_date,
            )
        )
        count, total_pnl, avg_pnl = result.one()

        return {
            "total_trades": count or 0,
            "total_pnl": float(total_pnl or 0),
            "average_pnl": float(avg_pnl or 0),
        }

    async def get_pnl_summary(self, user_id: int, period: str = "30d") -> dict:
        """Get P&L summary."""
        days = self._parse_period(period)
        start_date = datetime.now(timezone.utc) - __import__("datetime").timedelta(days=days)

        result = await self.db.execute(
            select(func.sum(Trade.pnl)).where(
                Trade.user_id == user_id,
                Trade.executed_at >= start_date,
            )
        )
        total_pnl = result.scalar() or 0

        return {
            "period": period,
            "total_pnl": float(total_pnl),
        }

    def _parse_period(self, period: str) -> int:
        """Parse period string to days."""
        unit = period[-1]
        value = int(period[:-1])
        multipliers = {"d": 1, "w": 7, "m": 30, "y": 365}
        return value * multipliers.get(unit, 30)


class PortfolioRepository(BaseRepository[PortfolioSnapshot]):
    """Repository for portfolio snapshots."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, PortfolioSnapshot)

    async def get_snapshots(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[PortfolioSnapshot]:
        """Get portfolio snapshots."""
        query = select(PortfolioSnapshot).where(
            PortfolioSnapshot.user_id == user_id
        )

        if start_date:
            query = query.where(PortfolioSnapshot.created_at >= start_date)
        if end_date:
            query = query.where(PortfolioSnapshot.created_at <= end_date)

        query = query.order_by(PortfolioSnapshot.created_at.asc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_latest_snapshot(
        self, user_id: int
    ) -> Optional[PortfolioSnapshot]:
        """Get latest portfolio snapshot."""
        result = await self.db.execute(
            select(PortfolioSnapshot)
            .where(PortfolioSnapshot.user_id == user_id)
            .order_by(PortfolioSnapshot.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
