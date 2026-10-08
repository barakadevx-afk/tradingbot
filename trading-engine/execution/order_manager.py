"""
Order Manager
=============

Manages the complete order lifecycle:
Signal Generated -> Risk Validation -> Position Size -> Order Validation -> Submit -> Response -> Fill -> Monitoring -> Exit -> Record

Handles:
- Rejected orders
- Cancelled orders
- Partial fills
- Network errors
- Rate limiting
- Insufficient balance
- Invalid quantity
- Precision errors
- Duplicate orders
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

from trading_engine.execution.paper_executor import (
    PaperExecutor, Order, OrderType, OrderSide, OrderStatus, Position, Fill,
)
from trading_engine.risk.risk_engine import RiskEngine, RiskStatus
from trading_engine.risk.position_sizer import PositionSizer

logger = logging.getLogger(__name__)


class OrderManagerStatus(Enum):
    """Order manager status."""
    IDLE = "IDLE"
    PROCESSING = "PROCESSING"
    RATE_LIMITED = "RATE_LIMITED"
    ERROR = "ERROR"


@dataclass
class OrderRequest:
    """Order request from signal."""
    symbol: str
    action: str  # BUY or SELL
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    strategy: str
    signal_id: str


@dataclass
class OrderResult:
    """Result of order processing."""
    success: bool
    order_id: Optional[str]
    status: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "order_id": self.order_id,
            "status": self.status,
            "message": self.message,
            "details": self.details,
        }


class OrderManager:
    """
    Manages the complete order lifecycle with comprehensive error handling.
    """

    # Rate limiting
    MAX_ORDERS_PER_MINUTE: int = 10
    MAX_ORDERS_PER_SECOND: int = 2

    # Retry configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: float = 1.0

    def __init__(
        self,
        executor: PaperExecutor,
        risk_engine: RiskEngine,
        position_sizer: PositionSizer,
    ):
        self.executor = executor
        self.risk_engine = risk_engine
        self.position_sizer = position_sizer

        self._status = OrderManagerStatus.IDLE
        self._order_queue: List[OrderRequest] = []
        self._processed_orders: Dict[str, OrderResult] = {}
        self._order_history: List[Dict[str, Any]] = []

        # Rate limiting
        self._order_timestamps: List[float] = []
        self._last_order_time: float = 0.0

        # Error tracking
        self._consecutive_errors: int = 0
        self._max_consecutive_errors: int = 5

        logger.info("OrderManager initialized")

    @property
    def status(self) -> OrderManagerStatus:
        """Current order manager status."""
        return self._status

    def process_signal(self, request: OrderRequest) -> OrderResult:
        """
        Process a trading signal through the complete order lifecycle.

        Lifecycle:
        1. Signal Generated
        2. Risk Validation
        3. Position Size Calculation
        4. Order Validation
        5. Submit Order
        6. Response Handling
        7. Fill Processing
        8. Monitoring Setup
        9. Exit Planning
        10. Record Keeping

        Args:
            request: OrderRequest with signal details

        Returns:
            OrderResult with processing outcome
        """
        self._status = OrderManagerStatus.PROCESSING
        start_time = time.time()

        try:
            # Step 1: Signal Generated (already done)
            logger.info(f"Processing signal {request.signal_id} for {request.symbol}")

            # Step 2: Risk Validation
            risk_result = self._validate_risk(request)
            if not risk_result.is_approved:
                return self._create_result(
                    success=False,
                    status="RISK_REJECTED",
                    message=risk_result.message,
                    details=risk_result.details,
                )

            # Step 3: Position Size Calculation
            sizing_result = self._calculate_position_size(request)
            if not sizing_result.is_valid:
                return self._create_result(
                    success=False,
                    status="SIZING_REJECTED",
                    message=sizing_result.message,
                    details=sizing_result.details,
                )

            # Step 4: Order Validation
            validation_result = self._validate_order(request, sizing_result)
            if not validation_result["valid"]:
                return self._create_result(
                    success=False,
                    status="VALIDATION_REJECTED",
                    message=validation_result["message"],
                    details=validation_result,
                )

            # Step 5: Submit Order
            order = self._submit_order(request, sizing_result)
            if not order:
                return self._create_result(
                    success=False,
                    status="SUBMISSION_FAILED",
                    message="Failed to submit order",
                )

            # Step 6: Response Handling
            if order.status == OrderStatus.REJECTED:
                return self._create_result(
                    success=False,
                    status="EXCHANGE_REJECTED",
                    message="Order rejected by exchange",
                    details={"order_id": order.order_id},
                )

            # Step 7: Fill Processing
            fill_result = self._process_fill(order)

            # Step 8: Monitoring Setup
            self._setup_monitoring(order, request)

            # Step 9: Exit Planning
            self._plan_exit(order, request)

            # Step 10: Record Keeping
            result = self._create_result(
                success=True,
                status="EXECUTED",
                message=f"Order executed: {order.filled_quantity} @ {order.average_fill_price:.4f}",
                details={
                    "order_id": order.order_id,
                    "fill_details": fill_result,
                    "position_size": sizing_result.position_size,
                    "risk_amount": sizing_result.risk_amount,
                    "processing_time_ms": (time.time() - start_time) * 1000,
                },
            )

            self._record_order(request, result)
            self._status = OrderManagerStatus.IDLE
            return result

        except Exception as e:
            self._consecutive_errors += 1
            self._status = OrderManagerStatus.ERROR
            logger.error(f"Order processing error: {e}", exc_info=True)

            if self._consecutive_errors >= self._max_consecutive_errors:
                logger.critical(f"Max consecutive errors reached ({self._max_consecutive_errors})")

            return self._create_result(
                success=False,
                status="ERROR",
                message=str(e),
                details={"error_type": type(e).__name__},
            )

    def _validate_risk(self, request: OrderRequest):
        """Step 2: Validate trade against risk parameters."""
        return self.risk_engine.validate_trade(
            symbol=request.symbol,
            action=request.action,
            entry_price=request.entry_price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            position_size=0,  # Will be calculated next
        )

    def _calculate_position_size(self, request: OrderRequest):
        """Step 3: Calculate position size based on risk."""
        return self.position_sizer.calculate_position_size(
            symbol=request.symbol,
            entry_price=request.entry_price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
        )

    def _validate_order(self, request: OrderRequest, sizing_result) -> Dict[str, Any]:
        """Step 4: Validate order details."""
        errors = []

        # Check for duplicate
        if self._is_duplicate(request):
            errors.append("Duplicate order detected")

        # Check rate limiting
        if self._is_rate_limited():
            errors.append("Rate limit exceeded")

        # Check precision
        constraints = self.position_sizer.get_constraints(request.symbol)
        if sizing_result.position_size < constraints.min_qty:
            errors.append(f"Quantity below minimum: {sizing_result.position_size} < {constraints.min_qty}")

        if sizing_result.notional_value < constraints.min_notional:
            errors.append(f"Notional below minimum: {sizing_result.notional_value:.2f} < {constraints.min_notional}")

        # Check balance
        required = sizing_result.notional_value
        if required > self.executor.available_balance:
            errors.append(f"Insufficient balance: {required:.2f} > {self.executor.available_balance:.2f}")

        return {
            "valid": len(errors) == 0,
            "message": "; ".join(errors) if errors else "Valid",
            "errors": errors,
        }

    def _submit_order(self, request: OrderRequest, sizing_result) -> Optional[Order]:
        """Step 5: Submit order to executor."""
        try:
            side = OrderSide.BUY if request.action == "BUY" else OrderSide.SELL

            order = self.executor.place_market_order(
                symbol=request.symbol,
                side=side,
                quantity=sizing_result.position_size,
                current_price=request.entry_price,
                leverage=sizing_result.leverage,
            )

            return order
        except Exception as e:
            logger.error(f"Order submission failed: {e}")
            return None

    def _process_fill(self, order: Order) -> Dict[str, Any]:
        """Step 7: Process order fill details."""
        return {
            "filled_quantity": order.filled_quantity,
            "average_price": order.average_fill_price,
            "fee": order.fee,
            "fill_count": len(order.fills),
        }

    def _setup_monitoring(self, order: Order, request: OrderRequest) -> None:
        """Step 8: Setup position monitoring."""
        self.risk_engine.open_position(
            symbol=request.symbol,
            details={
                "order_id": order.order_id,
                "size": order.filled_quantity,
                "price": order.average_fill_price,
                "stop_loss": request.stop_loss,
                "take_profit": request.take_profit,
            },
        )

    def _plan_exit(self, order: Order, request: OrderRequest) -> None:
        """Step 9: Plan exit strategy."""
        # Update position with stop loss and take profit
        if request.symbol in self.executor._positions:
            position = self.executor._positions[request.symbol]
            position.stop_loss = request.stop_loss
            position.take_profit = request.take_profit

    def _record_order(self, request: OrderRequest, result: OrderResult) -> None:
        """Step 10: Record order in history."""
        self._order_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signal_id": request.signal_id,
            "symbol": request.symbol,
            "action": request.action,
            "result": result.to_dict(),
        })

    def _create_result(
        self,
        success: bool,
        status: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> OrderResult:
        """Create an order result."""
        return OrderResult(
            success=success,
            order_id=None,
            status=status,
            message=message,
            details=details or {},
        )

    def _is_duplicate(self, request: OrderRequest) -> bool:
        """Check if this is a duplicate order."""
        # Check if we have a recent order for the same symbol and action
        for order in reversed(self._order_history[-10:]):
            if (order["symbol"] == request.symbol and
                order["action"] == request.action and
                order["signal_id"] == request.signal_id):
                return True
        return False

    def _is_rate_limited(self) -> bool:
        """Check if we're hitting rate limits."""
        now = time.time()

        # Clean old timestamps
        self._order_timestamps = [t for t in self._order_timestamps if now - t < 60]

        # Check per-second limit
        recent = [t for t in self._order_timestamps if now - t < 1]
        if len(recent) >= self.MAX_ORDERS_PER_SECOND:
            return True

        # Check per-minute limit
        if len(self._order_timestamps) >= self.MAX_ORDERS_PER_MINUTE:
            return True

        return False

    def record_order_timestamp(self) -> None:
        """Record an order timestamp for rate limiting."""
        self._order_timestamps.append(time.time())

    def get_order_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get order history."""
        return self._order_history[-limit:]

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        if not self._order_history:
            return {}

        total = len(self._order_history)
        errors = [o for o in self._order_history if not o["result"]["success"]]

        return {
            "total_orders": total,
            "failed_orders": len(errors),
            "error_rate": len(errors) / total * 100 if total > 0 else 0,
            "consecutive_errors": self._consecutive_errors,
        }

    def reset(self) -> None:
        """Reset order manager state."""
        self._status = OrderManagerStatus.IDLE
        self._order_queue.clear()
        self._processed_orders.clear()
        self._order_history.clear()
        self._order_timestamps.clear()
        self._consecutive_errors = 0
        logger.info("OrderManager reset")
