"""JWT token handler."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

from jose import JWTError, jwt

from app.core.config import settings


class JWTHandler:
    """Handler for JWT token creation and validation."""

    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        self.refresh_token_expire = timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

    def create_access_token(
        self,
        subject: str,
        extra_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new access token."""
        expire = datetime.now(timezone.utc) + self.access_token_expire

        payload: Dict[str, Any] = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        if extra_claims:
            payload.update(extra_claims)

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, subject: str) -> str:
        """Create a new refresh token."""
        expire = datetime.now(timezone.utc) + self.refresh_token_expire

        payload = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_token_pair(
        self,
        subject: str,
        extra_claims: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, str]:
        """Create both access and refresh tokens."""
        access_token = self.create_access_token(subject, extra_claims)
        refresh_token = self.create_refresh_token(subject)
        return access_token, refresh_token

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a token."""
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return payload
        except JWTError:
            return None

    def verify_token(
        self, token: str, expected_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Verify a token and optionally check its type."""
        payload = self.decode_token(token)

        if payload is None:
            return None

        if expected_type and payload.get("type") != expected_type:
            return None

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            return None

        return payload

    def get_subject(self, token: str) -> Optional[str]:
        """Get the subject from a token."""
        payload = self.decode_token(token)
        return payload.get("sub") if payload else None

    def is_token_expired(self, token: str) -> bool:
        """Check if a token is expired."""
        payload = self.decode_token(token)
        if not payload:
            return True

        exp = payload.get("exp")
        if not exp:
            return True

        return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)


# Global JWT handler instance
jwt_handler = JWTHandler()
