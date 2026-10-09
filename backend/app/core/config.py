"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import List, Optional

from pydantic import EmailStr, Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "BARAKA AI Trading Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    SECRET_KEY: str = Field(..., min_length=32)
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Database
    POSTGRES_USER: str = "baraka"
    POSTGRES_PASSWORD: str = "baraka_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "baraka_trading"
    DATABASE_URL: Optional[str] = None
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[RedisDsn] = None

    # JWT
    JWT_SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ADMIN_EMAIL: Optional[EmailStr] = None
    ADMIN_PASSWORD: Optional[str] = Field(None, min_length=12)

    # Trading
    DEFAULT_LEVERAGE: float = 1.0
    MAX_LEVERAGE: float = 100.0
    DEFAULT_RISK_PER_TRADE: float = 0.01
    MAX_RISK_PER_TRADE: float = 0.05
    MAX_DAILY_LOSS: float = 0.03
    MAX_POSITION_SIZE: float = 0.1
    MIN_ORDER_SIZE: float = 0.001
    PAPER_TRADING_DEFAULT_BALANCE: float = 100000.0
    KILL_SWITCH_ENABLED: bool = False

    # Exchange
    EXCHANGE_API_KEY: Optional[str] = None
    EXCHANGE_API_SECRET: Optional[str] = None
    EXCHANGE_SANDBOX: bool = True
    DEFAULT_EXCHANGE: str = "binance"

    # AI/ML
    MODEL_PATH: str = "./models"
    AI_PREDICTION_THRESHOLD: float = 0.65
    AI_RETRAIN_INTERVAL_HOURS: int = 24
    AI_FEATURE_WINDOW: int = 50

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 1000

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v, info):
        if isinstance(v, str):
            return v
        values = info.data
        return f"sqlite:///./baraka.db"

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v, info):
        if isinstance(v, str):
            return v
        values = info.data
        password = values.get("REDIS_PASSWORD")
        auth = f":{password}@" if password else ""
        return f"redis://{auth}{values.get('REDIS_HOST', 'localhost')}:{values.get('REDIS_PORT', 6379)}/{values.get('REDIS_DB', 0)}"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def async_database_url(self) -> str:
        url = str(self.DATABASE_URL)
        return url.replace("postgresql+asyncpg", "postgresql+asyncpg")

    @property
    def sync_database_url(self) -> str:
        url = str(self.DATABASE_URL)
        for prefix in (
            "postgres://",
            "postgresql://",
            "postgresql+asyncpg://",
            "postgresql+psycopg2://",
        ):
            if url.startswith(prefix):
                return url.replace(prefix, "postgresql+psycopg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
