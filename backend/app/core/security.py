"""Security utilities for password hashing and JWT token management."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    import hashlib, base64
    # Check if it's a base64-encoded SHA256 hash (our format)
    try:
        decoded = base64.b64decode(hashed_password)
        if len(decoded) == 32:  # SHA256 hash length
            # Generate hash with same method (note: this is simplified)
            # In production, use proper salt storage
            test_hash = base64.b64encode(hashlib.pbkdf2_hmac('sha256', plain_password[:72].encode(), b'baraka_salt', 100000)).decode()
            return test_hash == hashed_password
    except Exception:
        pass
    # Fallback to passlib/bcrypt
    try:
        return pwd_context.verify(plain_password[:72], hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt (truncate to 72 bytes for compatibility)."""
    return pwd_context.hash(password[:72])


def create_access_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: Dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "type": "access",
        "iat": datetime.now(timezone.utc),
    }

    if extra_claims:
        to_encode.update(extra_claims)

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, int],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT refresh token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode: Dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
    }

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_token_pair(
    subject: Union[str, int], extra_claims: Optional[Dict[str, Any]] = None
) -> Tuple[str, str]:
    """Create both access and refresh tokens."""
    access_token = create_access_token(subject, extra_claims=extra_claims)
    refresh_token = create_refresh_token(subject)
    return access_token, refresh_token


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_token_type(payload: Dict[str, Any], expected_type: str) -> bool:
    """Verify the token type matches expected type."""
    return payload.get("type") == expected_type


def get_token_expiry(token: str) -> Optional[datetime]:
    """Get the expiry datetime from a token."""
    payload = decode_token(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    return None
