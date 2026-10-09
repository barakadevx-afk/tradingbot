"""Admin user configuration and initialization."""

import logging
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User

logger = logging.getLogger(__name__)

# Admin credentials
ADMIN_EMAIL = "barakatrader@gmail.com"
ADMIN_PASSWORD = "Baraka@2050!!!"
ADMIN_FULL_NAME = "BARAKA Admin"
ADMIN_ROLE = "SUPER_ADMIN"


def create_admin_user(db: Session) -> User:
    """Create the default admin user if it doesn't exist."""
    # Check if admin already exists
    existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if existing:
        logger.info("Admin user already exists")
        return existing

    # Create admin user
    admin = User(
        email=ADMIN_EMAIL,
        hashed_password=get_password_hash(ADMIN_PASSWORD),
        full_name=ADMIN_FULL_NAME,
        role=ADMIN_ROLE,
        is_active=True,
        is_2fa_enabled=False,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    logger.info("Admin user created successfully")
    return admin


def verify_admin_credentials(email: str, password: str) -> bool:
    """Verify admin credentials."""
    return email == ADMIN_EMAIL and password == ADMIN_PASSWORD
