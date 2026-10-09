"""Admin user configuration and initialization."""

import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User

logger = logging.getLogger(__name__)

def provision_admin_user(db: Session) -> None:
    """Create or rotate the initial admin account from private environment settings."""
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        if settings.is_production:
            logger.warning(
                "ADMIN_EMAIL and ADMIN_PASSWORD are not configured; "
                "skipping initial administrator provisioning"
            )
        return

    admin = db.query(User).filter(User.email == str(settings.ADMIN_EMAIL)).first()
    if admin and admin.role not in {"ADMIN", "SUPER_ADMIN"}:
        raise RuntimeError("Configured ADMIN_EMAIL belongs to a non-admin user")

    if admin is None:
        admin = User(
            email=str(settings.ADMIN_EMAIL),
            full_name="BARAKA Admin",
            role="SUPER_ADMIN",
            is_active=True,
            is_2fa_enabled=False,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
        )
        db.add(admin)
        logger.info("Initial admin account created")
    else:
        admin.hashed_password = get_password_hash(settings.ADMIN_PASSWORD)
        admin.is_active = True
        admin.role = "SUPER_ADMIN"
        logger.info("Initial admin credentials synchronized from environment")

    db.commit()
