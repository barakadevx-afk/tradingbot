"""Alert generation and management service."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import Alert
from app.repositories.system import AlertRepository
from app.services.market_data import MarketDataService


class AlertService:
    """Service for generating and managing alerts."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.alert_repo = AlertRepository(db)
        self.market_data = MarketDataService()

    async def create_alert(
        self,
        alert_type: str,
        title: str,
        message: str,
        severity: str = "info",
        user_id: Optional[int] = None,
        symbol: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Alert:
        """Create a new alert."""
        alert = await self.alert_repo.create(
            {
                "user_id": user_id,
                "alert_type": alert_type,
                "title": title,
                "message": message,
                "severity": severity,
                "symbol": symbol,
                "triggered_at": datetime.now(timezone.utc),
                "metadata_json": str(metadata) if metadata else None,
            },
        )
        return alert

    async def get_alerts(
        self,
        user_id: Optional[int] = None,
        alert_type: Optional[str] = None,
        severity: Optional[str] = None,
        is_read: Optional[bool] = None,
        is_dismissed: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Alert]:
        """Get alerts with filters."""
        return await self.alert_repo.get_alerts(
            user_id=user_id,
            alert_type=alert_type,
            severity=severity,
            is_read=is_read,
            is_dismissed=is_dismissed,
            limit=limit,
            offset=offset,
        )

    async def get_alert(self, alert_id: int) -> Optional[Alert]:
        """Get a specific alert."""
        return await self.alert_repo.get_by_id(alert_id)

    async def mark_as_read(self, alert_id: int) -> Alert:
        """Mark an alert as read."""
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise ValueError("Alert not found")

        return await self.alert_repo.update(alert_id, {"is_read": True})

    async def dismiss_alert(self, alert_id: int) -> Alert:
        """Dismiss an alert."""
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise ValueError("Alert not found")

        return await self.alert_repo.update(
            alert_id,
            {
                "is_dismissed": True,
                "dismissed_at": datetime.now(timezone.utc),
            },
        )

    async def mark_all_as_read(self, user_id: int) -> Dict:
        """Mark all alerts as read for a user."""
        result = await self.db.execute(
            update(Alert)
            .where(Alert.user_id == user_id, Alert.is_read == False)
            .values(is_read=True)
        )
        await self.db.commit()

        return {"updated_count": result.rowcount}

    async def dismiss_all(self, user_id: int) -> Dict:
        """Dismiss all alerts for a user."""
        result = await self.db.execute(
            update(Alert)
            .where(Alert.user_id == user_id, Alert.is_dismissed == False)
            .values(is_dismissed=True, dismissed_at=datetime.now(timezone.utc))
        )
        await self.db.commit()

        return {"updated_count": result.rowcount}

    async def delete_alert(self, alert_id: int) -> Dict:
        """Delete an alert."""
        alert = await self.alert_repo.get_by_id(alert_id)
        if not alert:
            raise ValueError("Alert not found")

        await self.alert_repo.delete(alert_id)
        return {"message": "Alert deleted"}

    async def check_price_alerts(self, symbol: str, current_price: float) -> List[Alert]:
        """Check and trigger price alerts."""
        # Get active price alerts for this symbol
        alerts = await self.alert_repo.get_alerts(
            alert_type="price",
            symbol=symbol,
            is_dismissed=False,
        )

        triggered = []
        for alert in alerts:
            # Parse metadata for price conditions
            if alert.metadata_json:
                import json
                try:
                    metadata = json.loads(alert.metadata_json)
                    target_price = metadata.get("target_price")
                    condition = metadata.get("condition")  # above or below

                    if target_price and condition:
                        should_trigger = False
                        if condition == "above" and current_price >= target_price:
                            should_trigger = True
                        elif condition == "below" and current_price <= target_price:
                            should_trigger = True

                        if should_trigger:
                            triggered.append(alert)
                except json.JSONDecodeError:
                    continue

        return triggered

    async def generate_signal_alert(self, signal: Dict) -> Alert:
        """Generate an alert from a trading signal."""
        return await self.create_alert(
            alert_type="signal",
            title=f"{signal['signal_type'].upper()} Signal: {signal['symbol']}",
            message=f"AI generated {signal['signal_type']} signal for {signal['symbol']} with {signal['confidence']*100:.1f}% confidence",
            severity="info" if signal["signal_type"] == "hold" else "warning",
            symbol=signal["symbol"],
            metadata=signal,
        )

    async def generate_risk_alert(self, user_id: int, risk_type: str, message: str) -> Alert:
        """Generate a risk-related alert."""
        return await self.create_alert(
            alert_type="risk",
            title=f"Risk Alert: {risk_type}",
            message=message,
            severity="critical",
            user_id=user_id,
        )

    async def get_unread_count(self, user_id: int) -> int:
        """Get count of unread alerts."""
        return await self.alert_repo.get_unread_count(user_id)

    async def cleanup_old_alerts(self, days: int = 30) -> int:
        """Clean up old dismissed alerts."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return await self.alert_repo.delete_old_alerts(cutoff)
