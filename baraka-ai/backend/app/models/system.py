"""System-related database models."""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)  # INFO, WARNING, CRITICAL
    message = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(36), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    algorithm = Column(String(50), nullable=False)  # logistic_regression, random_forest, etc.
    status = Column(String(20), default="DRAFT")  # DRAFT, TESTING, APPROVED, PRODUCTION, RETIRED
    training_start = Column(DateTime(timezone=True), nullable=True)
    training_end = Column(DateTime(timezone=True), nullable=True)
    features = Column(Text, nullable=True)  # JSON array
    parameters = Column(Text, nullable=True)  # JSON object
    metrics = Column(Text, nullable=True)  # JSON object
    dataset_period = Column(String(100), nullable=True)
    strategy_association = Column(String(50), nullable=True)
    drift_status = Column(String(20), default="STABLE")  # STABLE, WARNING, DRIFTED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(36), ForeignKey("model_versions.model_id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    buy_probability = Column(Float, nullable=False)
    sell_probability = Column(Float, nullable=False)
    hold_probability = Column(Float, nullable=False)
    expected_return = Column(Float, nullable=True)
    expected_volatility = Column(Float, nullable=True)
    market_regime = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    features_used = Column(Text, nullable=True)  # JSON object
    created_at = Column(DateTime(timezone=True), server_default=func.now())
