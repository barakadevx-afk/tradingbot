"""
Take Profit Calculator
======================

Provides multiple take profit calculation methods:
- Fixed risk/Reward ratio
- ATR-based target
- Resistance/Support target
- Partial take profit levels (1R, 2R, 3R)
- Trailing stop
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class TakeProfitResult:
    """Result of take profit calculation."""
    take_profit: float
    risk_reward_ratio: float
    target_type: str
    reasoning: str
    partial_targets: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.partial_targets is None:
            self.partial_targets = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "take_profit": self.take_profit,
            "risk_reward_ratio": self.risk_reward_ratio,
            "target_type": self.target_type,
            "reasoning": self.reasoning,
            "partial_targets": self.partial_targets,
            "metadata": self.metadata,
        }


@dataclass
class PartialTakeProfit:
    """Partial take profit level."""
    level: int  # 1R, 2R, 3R, etc.
    price: float
    percentage: float  # Percentage of position to close
    risk_reward: float


class TakeProfitCalculator:
    """
    Calculates take profit levels using multiple methods.
    """

    # Default risk/reward ratios
    DEFAULT_RR: float = 2.0
    MIN_RR: float = 1.5

    # ATR multiplier for target
    ATR_MULTIPLIER: float = 3.0

    # Partial TP percentages
    PARTIAL_TP_LEVELS: List[Tuple[int, float]] = [
        (1, 0.33),  # Close 33% at 1R
        (2, 0.33),  # Close 33% at 2R
        (3, 0.34),  # Close 34% at 3R
    ]

    def __init__(self):
        pass

    def calculate_fixed_rr(
        self,
        entry_price: float,
        stop_loss: float,
        action: str,
        rr_ratio: Optional[float] = None,
    ) -> TakeProfitResult:
        """
        Calculate take profit based on fixed risk/reward ratio.

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            action: 'BUY' or 'SELL'
            rr_ratio: Risk/reward ratio (default 2.0)

        Returns:
            TakeProfitResult with target price
        """
        rr = rr_ratio or self.DEFAULT_RR

        risk = abs(entry_price - stop_loss)
        reward = risk * rr

        if action == "BUY":
            take_profit = entry_price + reward
        else:
            take_profit = entry_price - reward

        return TakeProfitResult(
            take_profit=round(take_profit, 8),
            risk_reward_ratio=rr,
            target_type="fixed_rr",
            reasoning=f"Fixed R/R target: {rr}R",
            metadata={"risk": risk, "reward": reward},
        )

    def calculate_atr_target(
        self,
        entry_price: float,
        atr: float,
        action: str,
        multiplier: Optional[float] = None,
    ) -> TakeProfitResult:
        """
        Calculate ATR-based take profit target.

        Args:
            entry_price: Entry price
            atr: Current ATR value
            action: 'BUY' or 'SELL'
            multiplier: ATR multiplier (default 3.0)

        Returns:
            TakeProfitResult with target price
        """
        mult = multiplier or self.ATR_MULTIPLIER

        if action == "BUY":
            take_profit = entry_price + (atr * mult)
        else:
            take_profit = entry_price - (atr * mult)

        # Calculate R/R if stop loss is ATR-based
        stop_distance = atr * 2  # Assuming 2x ATR stop
        reward = abs(take_profit - entry_price)
        rr = reward / stop_distance if stop_distance > 0 else 0

        return TakeProfitResult(
            take_profit=round(take_profit, 8),
            risk_reward_ratio=rr,
            target_type="atr_target",
            reasoning=f"ATR target: {mult}x ATR ({atr:.4f})",
            metadata={"atr": atr, "multiplier": mult},
        )

    def calculate_sr_target(
        self,
        entry_price: float,
        support_levels: List[float],
        resistance_levels: List[float],
        action: str,
        stop_loss: float,
    ) -> TakeProfitResult:
        """
        Calculate support/resistance-based take profit target.

        Args:
            entry_price: Entry price
            support_levels: List of support prices
            resistance_levels: List of resistance prices
            action: 'BUY' or 'SELL'
            stop_loss: Stop loss price

        Returns:
            TakeProfitResult with target price
        """
        risk = abs(entry_price - stop_loss)

        if action == "BUY":
            # Target nearest resistance above entry
            valid_resistances = [r for r in resistance_levels if r > entry_price]
            if valid_resistances:
                target = min(valid_resistances)
                reward = target - entry_price
                rr = reward / risk if risk > 0 else 0
                reasoning = f"S/R target: resistance at {target:.4f}"
            else:
                # Fallback to fixed R/R
                return self.calculate_fixed_rr(entry_price, stop_loss, action)
        else:
            # Target nearest support below entry
            valid_supports = [s for s in support_levels if s < entry_price]
            if valid_supports:
                target = max(valid_supports)
                reward = entry_price - target
                rr = reward / risk if risk > 0 else 0
                reasoning = f"S/R target: support at {target:.4f}"
            else:
                return self.calculate_fixed_rr(entry_price, stop_loss, action)

        return TakeProfitResult(
            take_profit=round(target, 8),
            risk_reward_ratio=rr,
            target_type="sr_target",
            reasoning=reasoning,
            metadata={"risk": risk, "reward": reward},
        )

    def calculate_partial_tp(
        self,
        entry_price: float,
        stop_loss: float,
        action: str,
        rr_levels: Optional[List[Tuple[int, float]]] = None,
    ) -> TakeProfitResult:
        """
        Calculate partial take profit levels.

        Creates multiple take profit levels at 1R, 2R, 3R with
        specified position closing percentages.

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            action: 'BUY' or 'SELL'
            rr_levels: List of (R_level, close_percentage) tuples

        Returns:
            TakeProfitResult with partial targets
        """
        levels = rr_levels or self.PARTIAL_TP_LEVELS
        risk = abs(entry_price - stop_loss)

        partial_targets = []
        for r_level, close_pct in levels:
            reward = risk * r_level
            if action == "BUY":
                target_price = entry_price + reward
            else:
                target_price = entry_price - reward

            partial_targets.append({
                "level": r_level,
                "price": round(target_price, 8),
                "percentage": close_pct,
                "risk_reward": float(r_level),
            })

        # Primary target is the first level
        primary_target = partial_targets[0]["price"] if partial_targets else entry_price + risk * self.DEFAULT_RR

        return TakeProfitResult(
            take_profit=primary_target,
            risk_reward_ratio=float(partial_targets[0]["level"]) if partial_targets else self.DEFAULT_RR,
            target_type="partial_tp",
            reasoning=f"Partial TP: {len(partial_targets)} levels",
            partial_targets=partial_targets,
            metadata={"risk": risk, "levels": len(partial_targets)},
        )

    def calculate_trailing_stop(
        self,
        entry_price: float,
        current_price: float,
        atr: float,
        action: str,
        activation_rr: float = 1.0,
        trail_multiplier: float = 2.0,
    ) -> TakeProfitResult:
        """
        Calculate trailing stop take profit.

        Activates after reaching activation_rr and trails the price
        by trail_multiplier * ATR.

        Args:
            entry_price: Entry price
            current_price: Current market price
            atr: Current ATR value
            action: 'BUY' or 'SELL'
            activation_rr: R/R level to activate trailing
            trail_multiplier: ATR multiplier for trailing distance

        Returns:
            TakeProfitResult with trailing stop level
        """
        risk = abs(entry_price - (entry_price - atr * 2))  # Assuming 2x ATR stop
        activation_price = entry_price + (risk * activation_rr) if action == "BUY" else entry_price - (risk * activation_rr)

        # Check if trailing is activated
        if action == "BUY" and current_price >= activation_price:
            trail_distance = atr * trail_multiplier
            trailing_stop = current_price - trail_distance
            reasoning = f"Trailing stop activated at {activation_rr}R, trailing {trail_multiplier}x ATR"
        elif action == "SELL" and current_price <= activation_price:
            trail_distance = atr * trail_multiplier
            trailing_stop = current_price + trail_distance
            reasoning = f"Trailing stop activated at {activation_rr}R, trailing {trail_multiplier}x ATR"
        else:
            # Not activated yet, use fixed target
            return self.calculate_fixed_rr(entry_price, entry_price - atr * 2 if action == "BUY" else entry_price + atr * 2, action)

        return TakeProfitResult(
            take_profit=round(trailing_stop, 8),
            risk_reward_ratio=activation_rr,
            target_type="trailing_stop",
            reasoning=reasoning,
            metadata={
                "activation_rr": activation_rr,
                "trail_multiplier": trail_multiplier,
                "activation_price": activation_price,
            },
        )

    def get_optimal_target(
        self,
        entry_price: float,
        stop_loss: float,
        atr: float,
        support_levels: List[float],
        resistance_levels: List[float],
        action: str,
    ) -> TakeProfitResult:
        """
        Get the optimal take profit target.

        Compares fixed R/R, ATR, and S/R targets and selects
        the one with the best risk/reward that is still achievable.

        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            atr: Current ATR
            support_levels: Support levels
            resistance_levels: Resistance levels
            action: 'BUY' or 'SELL'

        Returns:
            TakeProfitResult with optimal target
        """
        targets = []

        # Fixed R/R target
        targets.append(self.calculate_fixed_rr(entry_price, stop_loss, action))

        # ATR target
        targets.append(self.calculate_atr_target(entry_price, atr, action))

        # S/R target
        targets.append(self.calculate_sr_target(entry_price, support_levels, resistance_levels, action, stop_loss))

        # Filter valid targets (must be on correct side of entry)
        if action == "BUY":
            valid_targets = [t for t in targets if t.take_profit > entry_price]
        else:
            valid_targets = [t for t in targets if t.take_profit < entry_price]

        if not valid_targets:
            return self.calculate_fixed_rr(entry_price, stop_loss, action)

        # Select target with highest R/R that is still reasonable (< 5R)
        reasonable_targets = [t for t in valid_targets if t.risk_reward_ratio <= 5.0]
        if reasonable_targets:
            optimal = max(reasonable_targets, key=lambda t: t.risk_reward_ratio)
        else:
            optimal = min(valid_targets, key=lambda t: t.risk_reward_ratio)

        optimal.reasoning = f"Optimal target: {optimal.reasoning}"
        return optimal
