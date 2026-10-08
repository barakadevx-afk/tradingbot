"""Seed script to populate the database with initial data."""

import asyncio
from datetime import datetime, timedelta, timezone

from app.core.security import get_password_hash
from app.db.base import create_tables, engine
from app.db.session import async_session_maker
from app.models.user import User
from app.models.system import RiskConfig, Strategy


async def seed_database():
    """Seed the database with initial data."""
    print("Creating tables...")
    await create_tables()

    async with async_session_maker() as session:
        # Create admin user
        admin = User(
            email="admin@baraka.ai",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role="admin",
            is_active=True,
        )
        session.add(admin)
        await session.flush()

        # Create trader user
        trader = User(
            email="trader@baraka.ai",
            hashed_password=get_password_hash("trader123"),
            full_name="Demo Trader",
            role="trader",
            is_active=True,
        )
        session.add(trader)
        await session.flush()

        # Create risk config for trader
        risk_config = RiskConfig(
            user_id=trader.id,
            max_position_size=0.1,
            max_daily_loss=0.03,
            max_total_loss=0.1,
            max_leverage=1.0,
            max_open_positions=5,
            risk_per_trade=0.01,
            max_drawdown=0.15,
        )
        session.add(risk_config)

        # Create sample strategy
        strategy = Strategy(
            user_id=trader.id,
            name="Trend Following",
            description="Basic trend following strategy using EMA crossovers",
            strategy_type="ai",
            symbols="BTC/USDT,ETH/USDT",
            timeframe="4h",
            parameters='{"ema_fast": 20, "ema_slow": 50}',
            is_active=True,
            is_paper=True,
        )
        session.add(strategy)

        await session.commit()
        print("✅ Database seeded successfully!")
        print(f"   Admin: admin@baraka.ai / admin123")
        print(f"   Trader: trader@baraka.ai / trader123")


if __name__ == "__main__":
    asyncio.run(seed_database())
