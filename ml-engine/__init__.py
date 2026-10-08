"""
BARAKA AI - ML Engine
=====================
Production-grade machine learning engine for algorithmic trading.

Provides feature engineering, model training, inference, registry management,
and monitoring capabilities.

Usage:
    from ml_engine import BARAKAAI

    ai = BARAKAAI()
    ai.train(data, target)
    prediction = ai.predict(latest_data)
"""

from ml_engine.features.feature_engineering import FeatureEngineer
from ml_engine.training.trainer import Trainer
from ml_engine.inference.predictor import Predictor
from ml_engine.registry.model_registry import ModelRegistry, ModelStatus
from ml_engine.monitoring.model_monitor import ModelMonitor

__version__ = "1.0.0"
__author__ = "BARAKA AI Team"

__all__ = [
    "BARAKAAI",
    "FeatureEngineer",
    "Trainer",
    "Predictor",
    "ModelRegistry",
    "ModelStatus",
    "ModelMonitor",
]


class BARAKAAI:
    """Main orchestrator for the BARAKA AI ML engine."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.feature_engineer = FeatureEngineer()
        self.trainer = Trainer(config=self.config.get("training"))
        self.predictor: Predictor | None = None
        self.registry = ModelRegistry(
            storage_path=self.config.get("registry_path", "models/registry")
        )
        self.monitor = ModelMonitor(
            registry=self.registry,
            config=self.config.get("monitoring"),
        )
        self._model = None
        self._model_info: dict | None = None

    def train(
        self,
        data,
        target_col: str = "target",
        feature_cols: list[str] | None = None,
        model_type: str = "xgboost",
        model_name: str = "baraka_model",
        strategy: str = "default",
        **kwargs,
    ) -> dict:
        """Train a new model and register it."""
        result = self.trainer.train(
            data=data,
            target_col=target_col,
            feature_cols=feature_cols,
            model_type=model_type,
            model_name=model_name,
            strategy=strategy,
            **kwargs,
        )
        self._model = result["model"]
        self._model_info = result["model_info"]
        self.predictor = Predictor(
            model=self._model,
            feature_engineer=self.feature_engineer,
            model_info=self._model_info,
        )
        return result

    def predict(self, data) -> dict:
        """Generate prediction from latest data."""
        if self.predictor is None:
            raise RuntimeError("No model loaded. Train or load a model first.")
        return self.predictor.predict(data)

    def load_model(self, model_id: str) -> None:
        """Load a model from the registry."""
        entry = self.registry.get(model_id)
        if entry is None:
            raise ValueError(f"Model '{model_id}' not found in registry.")
        if entry.status not in (ModelStatus.APPROVED, ModelStatus.PRODUCTION):
            raise ValueError(
                f"Model '{model_id}' has status '{entry.status.value}'. "
                "Only APPROVED or PRODUCTION models can be used for inference."
            )
        self._model = entry.load_model()
        self._model_info = entry.metadata
        self.predictor = Predictor(
            model=self._model,
            feature_engineer=self.feature_engineer,
            model_info=self._model_info,
        )

    def get_status(self) -> dict:
        """Get current engine status."""
        return {
            "model_loaded": self._model is not None,
            "model_info": self._model_info,
            "registry_count": len(self.registry.list_all()),
            "monitor_active": self.monitor.is_active,
        }
