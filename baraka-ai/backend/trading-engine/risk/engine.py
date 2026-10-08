"""Risk Management Engine - Has final authority over all trading decisions."""
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class RiskDecision(Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REDUCED = "REDUCED"


@dataclass
class RiskCheckResult:
    decision: RiskDecision
    reason: str
    max_position_size: Optional[float] = None
    adjusted_risk_percent: Optional[float] = None
    warnings: list = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class RiskEngine:
    """
    Risk Management Engine.
    
    This engine has FINAL AUTHORITY over all trading decisions.
    No trade can be executed without risk engine approval.
    """

    def __init__(self, config: dict):
        self.config = config
        self._kill_switch_active = config.get("kill_switch_active", False)
        self._consecutive_losses = config.get("consecutive_losses", 0)
        self._daily_loss_used = config.get("daily_loss_used", 0.0)
        self._weekly_loss_used = config.get("weekly_loss_used", 0.0)

    def evaluate_trade(
        self,
        signal: str,
        confidence: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        account_equity: float,
        current_exposure: float,
        open_positions: int,
        symbol: str,
        symbol_exposure: float,
    ) -> RiskCheckResult:
        """
        Evaluate a trade against all risk parameters.
        
        Returns RiskCheckResult with decision and details.
        """
        warnings = []

        # 1. Kill switch check - HIGHEST PRIORITY
        if self._kill_switch_active:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                reason="KILL SWITCH ACTIVE - All trading is blocked",
                warnings=["Kill switch must be deactivated before trading"]
            )

        # 2. Confidence threshold
        min_confidence = self.config.get("min_confidence", 0.70)
        if confidence < min_confidence:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                reason=f"Confidence {confidence:.1%} below minimum threshold {min_confidence:.1%}",
                warnings=["Wait for higher confidence signals"]
            )

        # 3. Risk/Reward check
        risk_amount = abs(entry_price - stop_loss)
        reward_amount = abs(take_profit - entry_price)
        if risk_amount > 0:
            rr_ratio = reward_amount / risk_amount
            min_rr = self.config.get("min_risk_reward", 1.5)
            if rr_ratio < min_rr:
                return RiskCheckResult(
                    decision=RiskDecision.REJECTED,
                    reason=f"Risk/Reward ratio {rr_ratio:.2f} below minimum {min_rr}",
                    warnings=["Look for better risk/reward opportunities"]
                )

        # 4. Daily loss limit
        max_daily_loss = self.config.get("max_daily_loss", 0.03)
        if self._daily_loss_used >= max_daily_loss:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                reason=f"Daily loss limit reached: {self._daily_loss_used:.2%} / {max_daily_loss:.2%}",
                warnings=["Trading paused for the day"]
            )

        # 5. Weekly loss limit
        max_weekly_loss = self.config.get("max_weekly_loss", 0.05)
        if self._weekly_loss_used >= max_weekly_loss:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                reason=f"Weekly loss limit reached: {self._weekly_loss_used:.2%} / {max_weekly_loss:.2%}",
                warnings=["Trading paused for the week"]
            )

        # 6. Max open positions
        max_positions = self.config.get("max_open_positions", 5)
        if open_positions >= max_positions:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                reason=f"Maximum open positions reached: {open_positions}/{max_positions}",
                warnings=["Close existing positions before opening new ones"]
            )

        # 7. Portfolio exposure limit
        max_exposure = self.config.get("max_portfolio_exposure", 0.80)
        new_exposure = current_exposure + (entry_price * self._calculate_position_size(
            account_equity, entry_price, stop_loss
        ))
        if new_exposure / account_equity > max_exposure:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                reason=f"Portfolio exposure would exceed limit: {new_exposure/account_equity:.1%} / {max_exposure:.1%}",
                warnings=["Reduce exposure before opening new positions"]
            )

        # 8. Symbol exposure limit
        max_symbol_exposure = self.config.get("max_symbol_exposure", 0.30)
        if symbol_exposure / account_equity > max_symbol_exposure:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                reason=f"Symbol exposure for {symbol} would exceed limit",
                warnings=["Diversify across symbols"]
            )

        # 9. Consecutive losses check
        max_consecutive = self.config.get("max_consecutive_losses", 5)
        adjusted_risk = self.config.get("risk_per_trade", 0.005)
        if self._consecutive_losses >= 3:
            adjusted_risk *= 0.5  # Reduce risk by half after 3 consecutive losses
            warnings.append(f"Risk reduced due to {self._consecutive_losses} consecutive losses")
        if self._consecutive_losses >= max_consecutive:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                reason=f"Maximum consecutive losses reached: {self._consecutive_losses}",
                warnings=["Strategy paused - review required before resuming"]
            )

        # 10. Leverage check
        max_leverage = self.config.get("max_leverage", 1)
        if max_leverage > 1:
            warnings.append(f"Leverage limited to {max_leverage}x")

        # Calculate position size
        position_size = self._calculate_position_size(
            account_equity, entry_price, stop_loss, adjusted_risk
        )

        # 11. Minimum position size check
        min_notional = 10.0  # $10 minimum
        if position_size * entry_price < min_notional:
            return RiskCheckResult(
                decision=RiskDecision.REJECTED,
                reason=f"Position size too small: ${position_size * entry_price:.2f} (min ${min_notional})",
                warnings=["Account balance too small for this trade"]
            )

        return RiskCheckResult(
            decision=RiskDecision.APPROVED,
            reason="Trade approved by risk engine",
            max_position_size=position_size,
            adjusted_risk_percent=adjusted_risk,
            warnings=warnings
        )

    def _calculate_position_size(
        self,
        account_equity: float,
        entry_price: float,
        stop_loss: float,
        risk_percent: Optional[float] = None
    ) -> float:
        """
        Calculate position size based on risk.
        
        Risk Amount = Account Equity × Risk Percentage
        Position Size = Risk Amount / Stop-Loss Distance
        """
        if risk_percent is None:
            risk_percent = self.config.get("risk_per_trade", 0.005)

        risk_amount = account_equity * risk_percent
        stop_distance = abs(entry_price - stop_loss)

        if stop_distance == 0:
            return 0

        position_size = risk_amount / stop_distance
        return position_size

    def update_after_trade(self, pnl: float, is_loss: bool):
        """Update risk state after a trade closes."""
        if is_loss:
            self._consecutive_losses += 1
            self._daily_loss_used += abs(pnl)
            self._weekly_loss_used += abs(pnl)
        else:
            self._consecutive_losses = 0

    def activate_kill_switch(self, reason: str):
        """Activate the emergency kill switch."""
        self._kill_switch_active = True
        return {
            "activated": True,
            "reason": reason,
            "timestamp": "now",
            "action": "All trading blocked. Manual reactivation required."
        }

    def deactivate_kill_switch(self):
        """Deactivate the kill switch (requires explicit action)."""
        self._kill_switch_active = False
        self._consecutive_losses = 0
        return {"activated": False, "message": "Kill switch deactivated"}

    def get_status(self) -> dict:
        """Get current risk engine status."""
        return {
            "kill_switch_active": self._kill_switch_active,
            "consecutive_losses": self._consecutive_losses,
            "daily_loss_used": self._daily_loss_used,
            "weekly_loss_used": self._weekly_loss_used,
            "max_daily_loss": self.config.get("max_daily_loss", 0.03),
            "max_weekly_loss": self.config.get("max_weekly_loss", 0.05),
            "max_consecutive_losses": self.config.get("max_consecutive_losses", 5),
            "risk_per_trade": self.config.get("risk_per_trade", 0.005),
            "min_confidence": self.config.get("min_confidence", 0.70),
        }
