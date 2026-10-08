\"\"\"Initialize BARAKA AI database with default data.\"\"\"
import asyncio
import sys
sys.path.insert(0, '.')

from app.db.base import Base, engine
from app.models.user import User
from app.models.system import RiskConfig, Strategy, ModelVersion
from app.core.security import get_password_hash


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('Database tables created successfully.')


async def create_admin():
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        admin = User(
            email='admin@baraka.ai',
            hashed_password=get_password_hash('AdminPass123!'),
            full_name='Admin User',
            role='SUPER_ADMIN',
            is_active=True,
            is_2fa_enabled=False,
        )
        session.add(admin)
        await session.commit()
        print('Admin user created: admin@baraka.ai / AdminPass123!')


async def create_defaults():
    from app.db.session import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        risk_config = RiskConfig(
            risk_per_trade=0.005,
            max_risk_per_trade=0.01,
            max_daily_loss=0.03,
            max_weekly_loss=0.05,
            max_drawdown=0.10,
            max_open_positions=5,
            max_leverage=1,
            max_portfolio_exposure=0.80,
            max_symbol_exposure=0.30,
            max_consecutive_losses=5,
            min_confidence=0.70,
            min_risk_reward=1.5,
        )
        session.add(risk_config)

        strategies = [
            Strategy(name='Trend Following', status='active', markets=['BTC/USDT', 'ETH/USDT'], timeframes=['4H', '1D']),
            Strategy(name='Breakout', status='active', markets=['BTC/USDT', 'ETH/USDT'], timeframes=['15M', '1H']),
            Strategy(name='Pullback', status='active', markets=['BTC/USDT', 'ETH/USDT'], timeframes=['1H', '4H']),
            Strategy(name='Mean Reversion', status='inactive', markets=['BTC/USDT', 'XRP/USDT'], timeframes=['1H', '4H']),
        ]
        for s in strategies:
            session.add(s)

        models = [
            ModelVersion(name='BARAKA Trend Predictor', version='v2.1.0', algorithm='XGBoost', status='PRODUCTION'),
            ModelVersion(name='BARAKA Momentum', version='v3.0.2', algorithm='LightGBM', status='APPROVED'),
            ModelVersion(name='BARAKA Range Detector', version='v1.2.0', algorithm='Random Forest', status='TESTING'),
        ]
        for m in models:
            session.add(m)

        await session.commit()
        print('Default data created.')


if __name__ == '__main__':
    asyncio.run(init_db())
    asyncio.run(create_admin())
    asyncio.run(create_defaults())
    print('BARAKA AI initialization complete.')
