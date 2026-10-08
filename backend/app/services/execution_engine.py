"""Execution engine for paper trading and order management."""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.trading import Order, Position, Trade
from app.models.user import User
from app.repositories.trading import OrderRepository, PositionRepository, TradeRepository
from app.repositories.user import UserRepository
from app.schemas.trading import OrderCreate
from app.services.market_data import MarketDataService
from app.services.risk_engine import RiskEngine


class ExecutionEngine:
    """Engine for executing trades in paper trading mode."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.order_repo = OrderRepository(db)
        self.position_repo = PositionRepository(db)
        self.trade_repo = TradeRepository(db)
        self.user_repo = UserRepository(db)
        self.market_data = MarketDataService()
        self.risk_engine = RiskEngine(db)
        self._paper_balances: Dict[int, float] = {}
        self._running_tasks: Dict[int, asyncio.Task] = {}

    async def start_paper_trading(self, user_id: int, initial_balance: float) -> Dict:
        """Start paper trading for a user."""
        self._paper_balances[user_id] = initial_balance

        # Start order monitoring task
        if user_id not in self._running_tasks:
            task = asyncio.create_task(self._monitor_orders(user_id))
            self._running_tasks[user_id] = task

        return {
            "status": "started",
            "user_id": user_id,
            "initial_balance": initial_balance,
            "message": "Paper trading started successfully",
        }

    async def stop_paper_trading(self, user_id: int) -> Dict:
        """Stop paper trading for a user."""
        if user_id in self._running_tasks:
            self._running_tasks[user_id].cancel()
            del self._running_tasks[user_id]

        return {
            "status": "stopped",
            "user_id": user_id,
            "message": "Paper trading stopped successfully",
        }

    async def get_paper_trading_status(self, user_id: int) -> Dict:
        """Get paper trading status."""
        is_running = user_id in self._running_tasks
        balance = self._paper_balances.get(user_id, settings.PAPER_TRADING_DEFAULT_BALANCE)

        return {
            "is_running": is_running,
            "user_id": user_id,
            "balance": balance,
            "mode": "paper",
        }

    async def get_paper_balance(self, user_id: int) -> Dict:
        """Get paper trading balance."""
        balance = self._paper_balances.get(user_id, settings.PAPER_TRADING_DEFAULT_BALANCE)

        # Calculate positions value
        positions_result = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.is_open == True,
            )
        )
        positions = positions_result.scalars().all()

        positions_value = sum(
            float(p.quantity) * float(p.entry_price) for p in positions
        )

        return {
            "cash_balance": round(balance, 2),
            "positions_value": round(positions_value, 2),
            "total_value": round(balance + positions_value, 2),
            "open_positions": len(positions),
        }

    async def reset_paper_trading(self, user_id: int, initial_balance: float) -> Dict:
        """Reset paper trading account."""
        # Stop if running
        if user_id in self._running_tasks:
            self._running_tasks[user_id].cancel()
            del self._running_tasks[user_id]

        # Close all positions
        await self.db.execute(
            update(Position)
            .where(Position.user_id == user_id, Position.is_open == True)
            .values(is_open=False, closed_at=datetime.now(timezone.utc))
        )

        # Reset balance
        self._paper_balances[user_id] = initial_balance

        await self.db.commit()

        return {
            "status": "reset",
            "user_id": user_id,
            "new_balance": initial_balance,
            "message": "Paper trading account reset successfully",
        }

    async def place_order(self, user_id: int, order_data: OrderCreate) -> Order:
        """Place a new order."""
        # Validate risk
        price = float(order_data.price) if order_data.price else await self.market_data.get_current_price(
            order_data.symbol
        )

        risk_check = await self.risk_engine.validate_trade(
            user_id=user_id,
            symbol=order_data.symbol,
            quantity=float(order_data.quantity),
            price=price,
            side=order_data.side,
        )

        if not risk_check["valid"]:
            raise ValueError(f"Risk validation failed: {risk_check['reason']}")

        # Create order
        order = await self.order_repo.create(
            {
                "user_id": user_id,
                "symbol": order_data.symbol,
                "order_type": order_data.order_type,
                "side": order_data.side,
                "quantity": order_data.quantity,
                "price": order_data.price,
                "stop_price": order_data.stop_price,
                "status": "open",
                "is_paper": order_data.is_paper,
                "signal_id": order_data.signal_id,
                "strategy_id": order_data.strategy_id,
                "placed_at": datetime.now(timezone.utc),
            }
        )

        # For market orders, execute immediately
        if order_data.order_type == "market":
            await self._execute_order(order)

        return order

    async def cancel_order(self, user_id: int, order_id: int) -> Dict:
        """Cancel an order."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")

        if order.user_id != user_id:
            raise ValueError("Not authorized to cancel this order")

        if order.status not in ("pending", "open"):
            raise ValueError(f"Cannot cancel order with status: {order.status}")

        await self.order_repo.update(
            order_id,
            {
                "status": "cancelled",
                "filled_at": datetime.now(timezone.utc),
            },
        )

        return {"message": f"Order {order_id} cancelled successfully"}

    async def cancel_all_orders(self, user_id: int, symbol: Optional[str] = None) -> Dict:
        """Cancel all open orders."""
        conditions = {
            "user_id": user_id,
            "status": "open",
        }
        if symbol:
            conditions["symbol"] = symbol

        result = await self.db.execute(
            update(Order)
            .where(
                Order.user_id == user_id,
                Order.status == "open",
                *( [Order.symbol == symbol] if symbol else [] )
            )
            .values(status="cancelled", filled_at=datetime.now(timezone.utc))
        )
        await self.db.commit()

        return {
            "cancelled_count": result.rowcount,
            "message": f"Cancelled {result.rowcount} orders",
        }

    async def close_position(self, user_id: int, position_id: int) -> Dict:
        """Close a position."""
        position = await self.position_repo.get_by_id(position_id)
        if not position:
            raise ValueError("Position not found")

        if position.user_id != user_id:
            raise ValueError("Not authorized to close this position")

        if not position.is_open:
            raise ValueError("Position is already closed")

        # Get current price
        current_price = await self.market_data.get_current_price(position.symbol)

        # Calculate P&L
        if position.side == "long":
            pnl = (current_price - float(position.entry_price)) * float(position.quantity)
        else:
            pnl = (float(position.entry_price) - current_price) * float(position.quantity)

        # Update position
        await self.position_repo.update(
            position_id,
            {
                "is_open": False,
                "closed_at": datetime.now(timezone.utc),
                "current_price": current_price,
                "realized_pnl": pnl,
            },
        )

        # Create trade record
        await self.trade_repo.create(
            {
                "user_id": user_id,
                "position_id": position_id,
                "symbol": position.symbol,
                "side": "sell" if position.side == "long" else "buy",
                "quantity": position.quantity,
                "price": current_price,
                "pnl": pnl,
                "is_paper": True,
                "executed_at": datetime.now(timezone.utc),
            }
        )

        # Update paper balance
        if user_id in self._paper_balances:
            self._paper_balances[user_id] += pnl

        return {
            "message": f"Position {position_id} closed",
            "pnl": round(pnl, 2),
            "closing_price": current_price,
        }

    async def close_all_positions(self, user_id: int, symbol: Optional[str] = None) -> Dict:
        """Close all positions."""
        conditions = {"user_id": user_id, "is_open": True}
        if symbol:
            conditions["symbol"] = symbol

        result = await self.db.execute(
            select(Position).where(
                Position.user_id == user_id,
                Position.is_open == True,
                *( [Position.symbol == symbol] if symbol else [] )
            )
        )
        positions = result.scalars().all()

        closed_count = 0
        total_pnl = 0

        for position in positions:
            close_result = await self.close_position(user_id, position.id)
            closed_count += 1
            total_pnl += close_result["pnl"]

        return {
            "closed_count": closed_count,
            "total_pnl": round(total_pnl, 2),
            "message": f"Closed {closed_count} positions",
        }

    async def _execute_order(self, order: Order) -> None:
        """Execute an order (paper trading)."""
        # Get current market price
        current_price = await self.market_data.get_current_price(order.symbol)

        # Simulate execution
        await self.order_repo.update(
            order.id,
            {
                "status": "filled",
                "filled_quantity": order.quantity,
                "average_fill_price": current_price,
                "filled_at": datetime.now(timezone.utc),
            },
        )

        # Create or update position
        await self._update_position(order, current_price)

        # Create trade record
        await self.trade_repo.create(
            {
                "user_id": order.user_id,
                "order_id": order.id,
                "symbol": order.symbol,
                "side": order.side,
                "quantity": order.quantity,
                "price": current_price,
                "is_paper": order.is_paper,
                "executed_at": datetime.now(timezone.utc),
            }
        )

    async def _update_position(self, order: Order, price: float) -> None:
        """Update or create position after order execution."""
        # Check for existing position
        result = await self.db.execute(
            select(Position).where(
                Position.user_id == order.user_id,
                Position.symbol == order.symbol,
                Position.is_open == True,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing position
            if existing.side == order.side:
                # Adding to position
                total_qty = float(existing.quantity) + float(order.quantity)
                avg_price = (
                    (float(existing.entry_price) * float(existing.quantity))
                    + (price * float(order.quantity))
                ) / total_qty
                await self.position_repo.update(
                    existing.id,
                    {
                        "quantity": total_qty,
                        "entry_price": avg_price,
                        "current_price": price,
                    },
                )
            else:
                # Reducing or closing position
                remaining = float(existing.quantity) - float(order.quantity)
                if remaining <= 0:
                    await self.position_repo.update(
                        existing.id,
                        {
                            "is_open": False,
                            "closed_at": datetime.now(timezone.utc),
                            "current_price": price,
                        },
                    )
                else:
                    await self.position_repo.update(
                        existing.id,
                        {
                            "quantity": remaining,
                            "current_price": price,
                        },
                    )
        else:
            # Create new position
            await self.position_repo.create(
                {
                    "user_id": order.user_id,
                    "symbol": order.symbol,
                    "side": order.side,
                    "quantity": order.quantity,
                    "entry_price": price,
                    "current_price": price,
                    "is_open": True,
                    "opened_at": datetime.now(timezone.utc),
                }
            )

    async def _monitor_orders(self, user_id: int) -> None:
        """Monitor open orders for execution."""
        while True:
            try:
                # Check for pending orders that can be executed
                result = await self.db.execute(
                    select(Order).where(
                        Order.user_id == user_id,
                        Order.status == "open",
                        Order.order_type != "market",
                    )
                )
                orders = result.scalars().all()

                for order in orders:
                    current_price = await self.market_data.get_current_price(order.symbol)

                    should_execute = False
                    if order.order_type == "limit":
                        if order.side == "buy" and current_price <= float(order.price):
                            should_execute = True
                        elif order.side == "sell" and current_price >= float(order.price):
                            should_execute = True
                    elif order.order_type == "stop_limit":
                        if order.stop_price:
                            if order.side == "buy" and current_price >= float(order.stop_price):
                                should_execute = True
                            elif order.side == "sell" and current_price <= float(order.stop_price):
                                should_execute = True

                    if should_execute:
                        await self._execute_order(order)

                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(5)
