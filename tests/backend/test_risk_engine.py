\"\"\"BARAKA AI - Risk Engine Tests\"\"\"
import pytest
import sys
sys.path.insert(0, '.')

from trading_engine.risk.risk_engine import RiskEngine
from trading_engine.risk.position_sizer import PositionSizer


def test_risk_engine_initialization():
    engine = RiskEngine()
    assert engine.config['risk_per_trade'] == 0.005
    assert engine.config['max_risk_per_trade'] == 0.01
    assert engine.config['max_daily_loss'] == 0.03
    assert engine.config['max_drawdown'] == 0.10


def test_position_sizing_basic():
    sizer = PositionSizer()
    result = sizer.calculate_position_size(
        equity=10000,
        risk_percent=0.005,
        entry_price=67000,
        stop_loss=66000
    )
    assert result['risk_amount'] == 50.0
    assert result['position_size'] > 0
    assert result['position_value'] > 0


def test_position_sizing_zero_balance():
    sizer = PositionSizer()
    result = sizer.calculate_position_size(
        equity=0,
        risk_percent=0.005,
        entry_price=67000,
        stop_loss=66000
    )
    assert result['position_size'] == 0


def test_position_sizing_invalid_stop():
    sizer = PositionSizer()
    result = sizer.calculate_position_size(
        equity=10000,
        risk_percent=0.005,
        entry_price=67000,
        stop_loss=67000
    )
    assert result['position_size'] == 0


def test_kill_switch_blocks_trading():
    engine = RiskEngine()
    engine.activate_kill_switch('Test activation')
    assert engine.is_kill_switch_active() == True
    assert engine.can_trade() == False


def test_drawdown_protection():
    engine = RiskEngine()
    engine.update_drawdown(0.11)
    assert engine.can_trade() == False


def test_daily_loss_limit():
    engine = RiskEngine()
    engine.update_daily_loss(0.035)
    assert engine.can_trade() == False


def test_consecutive_losses():
    engine = RiskEngine()
    for _ in range(5):
        engine.record_trade_result(-10)
    assert engine.get_consecutive_losses() == 5
    assert engine.can_trade() == False


def test_no_martingale():
    engine = RiskEngine()
    for _ in range(3):
        engine.record_trade_result(-10)
    size_after_losses = engine.get_risk_percent()
    assert size_after_losses <= engine.config['risk_per_trade']
