"""User repository."""

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user operations."""

    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == id).first()

    def create(
        self,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        role: str = "trader",
    ) -> User:
        """Create a new user."""
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_last_login(self, user_id: int) -> None:
        """Update last login timestamp."""
        user = self.get_by_id(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            self.db.commit()

    def update_password(self, user_id: int, hashed_password: str) -> None:
        """Update user password."""
        user = self.get_by_id(user_id)
        if user:
            user.hashed_password = hashed_password
            self.db.commit()

    def deactivate(self, user_id: int) -> None:
        """Deactivate a user."""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            self.db.commit()

    def activate(self, user_id: int) -> None:
        """Activate a user."""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = True
            self.db.commit()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users."""
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    def get_users_by_role(self, role: str) -> List[User]:
        """Get users by role."""
        return self.db.query(User).filter(User.role == role).all()
