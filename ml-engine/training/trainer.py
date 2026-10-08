"""
ML Training Pipeline
====================
Complete training pipeline for BARAKA AI models.

Supports:
- Logistic Regression
- Random Forest
- Gradient Boosting
- XGBoost (if installed)
- LightGBM (if installed)

Features:
- Chronological train/validation/test split
- Walk-forward validation
- Final evaluation with comprehensive metrics
- Model registration with full metadata
- Serialization support (joblib/pickle)
"""

from __future__ import annotations

import json
import logging
import pickle
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    log_loss,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler

from ml_engine.features.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)

# Optional imports
try:
    import xgboost as xgb

    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    logger.debug("XGBoost not installed. XGBoost models will not be available.")

try:
    import lightgbm as lgb

    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False
    logger.debug("LightGBM not installed. LightGBM models will not be available.")


@dataclass
class ModelInfo:
    """Complete metadata for a trained model."""

    model_id: str
    name: str
    version: str
    model_type: str
    strategy: str
    training_date: str
    features: list[str]
    parameters: dict[str, Any]
    metrics: dict[str, float]
    dataset_period: dict[str, str]
    dataset_size: int
    target_column: str
    class_distribution: dict[str, int]
    walk_forward_results: dict[str, Any] = field(default_factory=dict)
    feature_importances: dict[str, float] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)


class Trainer:
    """ML training pipeline for BARAKA AI.

    Handles the complete lifecycle from raw data to registered model:
    1. Data preparation and validation
    2. Feature engineering
    3. Chronological train/validation/test split
    4. Walk-forward validation
    5. Final model training
    6. Evaluation and registration
    """

    SUPPORTED_MODELS = ["logistic_regression", "random_forest", "gradient_boosting", "xgboost", "lightgbm"]

    DEFAULT_PARAMS: dict[str, dict[str, Any]] = {
        "logistic_regression": {
            "max_iter": 1000,
            "class_weight": "balanced",
            "solver": "lbfgs",
            "C": 1.0,
        },
        "random_forest": {
            "n_estimators": 200,
            "max_depth": 10,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "class_weight": "balanced",
            "random_state": 42,
            "n_jobs": -1,
        },
        "gradient_boosting": {
            "n_estimators": 200,
            "max_depth": 5,
            "learning_rate": 0.1,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "random_state": 42,
        },
        "xgboost": {
            "n_estimators": 200,
            "max_depth": 6,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "use_label_encoder": False,
            "eval_metric": "logloss",
        },
        "lightgbm": {
            "n_estimators": 200,
            "max_depth": 6,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42,
            "verbose": -1,
        },
    }

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the Trainer.

        Args:
            config: Configuration dictionary with optional keys:
                - test_size: Fraction for test set (default: 0.15)
                - val_size: Fraction for validation set (default: 0.15)
                - n_splits: Number of walk-forward splits (default: 5)
                - random_state: Random seed (default: 42)
                - model_dir: Directory to save models (default: "models")
                - scale_features: Whether to standardize features (default: True)
        """
        self.config = config or {}
        self.test_size = self.config.get("test_size", 0.15)
        self.val_size = self.config.get("val_size", 0.15)
        self.n_splits = self.config.get("n_splits", 5)
        self.random_state = self.config.get("random_state", 42)
        self.model_dir = Path(self.config.get("model_dir", "models"))
        self.scale_features = self.config.get("scale_features", True)

        self.feature_engineer = FeatureEngineer()
        self.scaler: StandardScaler | None = None
        self._model: Any = None
        self._model_info: ModelInfo | None = None

    def train(
        self,
        data: pd.DataFrame,
        target_col: str = "target",
        feature_cols: list[str] | None = None,
        model_type: str = "xgboost",
        model_name: str = "baraka_model",
        strategy: str = "default",
        custom_params: dict[str, Any] | None = None,
        notes: str = "",
    ) -> dict[str, Any]:
        """Execute the complete training pipeline.

        Args:
            data: DataFrame with OHLCV data and target column.
            target_col: Name of the target column (1=BUY, 0=HOLD, -1=SELL or 0/1/2).
            feature_cols: Specific features to use. If None, all engineered features.
            model_type: One of 'logistic_regression', 'random_forest',
                       'gradient_boosting', 'xgboost', 'lightgbm'.
            model_name: Human-readable name for the model.
            strategy: Strategy association (e.g., 'momentum', 'mean_reversion').
            custom_params: Override default model parameters.
            notes: Additional notes for the model registry.

        Returns:
            Dictionary with keys: 'model', 'model_info', 'metrics', 'walk_forward'.

        Raises:
            ValueError: If model_type is not supported or data is invalid.
        """
        logger.info(f"Starting training pipeline for '{model_name}' (type: {model_type})")

        # Validate inputs
        self._validate_inputs(data, target_col, model_type)

        # Step 1: Feature engineering
        logger.info("Step 1/6: Engineering features...")
        features_df = self.feature_engineer.fit_transform(data)

        # Combine with target
        full_df = pd.concat([features_df, data[[target_col]]], axis=1)

        # Drop rows with NaN values (from rolling calculations)
        initial_len = len(full_df)
        full_df = full_df.dropna()
        dropped = initial_len - len(full_df)
        if dropped > 0:
            logger.warning(f"Dropped {dropped} rows with NaN values ({dropped/initial_len*100:.1f}%)")

        if len(full_df) < 100:
            raise ValueError(
                f"Insufficient data after NaN removal: {len(full_df)} rows. "
                "Need at least 100 rows for training."
            )

        # Select features
        if feature_cols is None:
            feature_cols = [c for c in full_df.columns if c != target_col]
        else:
            missing = set(feature_cols) - set(full_df.columns)
            if missing:
                raise ValueError(f"Specified feature columns not found: {missing}")

        X = full_df[feature_cols].values
        y = full_df[target_col].values

        # Encode target if needed (-1, 0, 1 -> 0, 1, 2)
        y_encoded, class_map = self._encode_target(y)
        logger.info(f"Class mapping: {class_map}")
        logger.info(f"Class distribution: {np.bincount(y_encoded)}")

        # Step 2: Chronological split
        logger.info("Step 2/6: Splitting data chronologically...")
        splits = self._chronological_split(X, y_encoded)
        X_train, y_train = splits["train"]
        X_val, y_val = splits["val"]
        X_test, y_test = splits["test"]

        logger.info(
            f"Split sizes - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}"
        )

        # Step 3: Feature scaling
        if self.scale_features:
            logger.info("Step 3/6: Scaling features...")
            self.scaler = StandardScaler()
            X_train = self.scaler.fit_transform(X_train)
            X_val = self.scaler.transform(X_val)
            X_test = self.scaler.transform(X_test)
        else:
            logger.info("Step 3/6: Skipping feature scaling")

        # Step 4: Walk-forward validation
        logger.info("Step 4/6: Running walk-forward validation...")
        wf_results = self._walk_forward_validation(X_train, y_train, model_type, custom_params)
        logger.info(f"Walk-forward mean accuracy: {wf_results['mean_accuracy']:.4f}")

        # Step 5: Final training on train+val
        logger.info("Step 5/6: Training final model on train+val...")
        X_train_val = np.vstack([X_train, X_val])
        y_train_val = np.concatenate([y_train, y_val])

        model = self._create_model(model_type, custom_params)
        model.fit(X_train_val, y_train_val)
        self._model = model

        # Step 6: Final evaluation on test set
        logger.info("Step 6/6: Evaluating on test set...")
        metrics = self._evaluate(model, X_test, y_test, class_map)

        # Feature importances
        feature_importances = self._get_feature_importances(model, feature_cols)

        # Create model info
        model_id = str(uuid.uuid4())[:8]
        version = self._generate_version(model_name)

        # Determine dataset period
        if "timestamp" in data.columns:
            start_date = str(data["timestamp"].iloc[0])
            end_date = str(data["timestamp"].iloc[-1])
        elif "date" in data.columns:
            start_date = str(data["date"].iloc[0])
            end_date = str(data["date"].iloc[-1])
        else:
            start_date = "unknown"
            end_date = "unknown"

        class_distribution = {
            str(cls): int(count) for cls, count in zip(*np.unique(y, return_counts=True))
        }

        self._model_info = ModelInfo(
            model_id=model_id,
            name=model_name,
            version=version,
            model_type=model_type,
            strategy=strategy,
            training_date=datetime.now(timezone.utc).isoformat(),
            features=feature_cols,
            parameters=self._get_model_params(model, model_type),
            metrics=metrics,
            dataset_period={"start": start_date, "end": end_date},
            dataset_size=len(full_df),
            target_column=target_col,
            class_distribution=class_distribution,
            walk_forward_results=wf_results,
            feature_importances=feature_importances,
            notes=notes,
        )

        # Save model
        self._save_model(model, self._model_info)

        logger.info(f"Training complete. Model ID: {model_id}, Version: {version}")
        logger.info(f"Test Accuracy: {metrics['accuracy']:.4f}, F1: {metrics['f1_macro']:.4f}")

        return {
            "model": model,
            "model_info": self._model_info,
            "metrics": metrics,
            "walk_forward": wf_results,
        }

    def _validate_inputs(
        self, data: pd.DataFrame, target_col: str, model_type: str
    ) -> None:
        """Validate training inputs."""
        if data.empty:
            raise ValueError("Training data is empty.")

        if target_col not in data.columns:
            raise ValueError(f"Target column '{target_col}' not found in data.")

        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model type '{model_type}'. "
                f"Choose from: {self.SUPPORTED_MODELS}"
            )

        if model_type == "xgboost" and not HAS_XGBOOST:
            raise ValueError("XGBoost is not installed. Install with: pip install xgboost")

        if model_type == "lightgbm" and not HAS_LIGHTGBM:
            raise ValueError("LightGBM is not installed. Install with: pip install lightgbm")

        # Check for minimum data
        if len(data) < 200:
            raise ValueError(
                f"Insufficient data: {len(data)} rows. Need at least 200 rows."
            )

    def _encode_target(self, y: np.ndarray) -> tuple[np.ndarray, dict[int, int]]:
        """Encode target labels to consecutive integers starting from 0.

        Handles both (-1, 0, 1) and (0, 1, 2) encodings.
        """
        unique_labels = np.unique(y)
        class_map = {int(label): idx for idx, label in enumerate(sorted(unique_labels))}
        y_encoded = np.array([class_map[int(label)] for label in y])
        return y_encoded, class_map

    def _chronological_split(
        self, X: np.ndarray, y: np.ndarray
    ) -> dict[str, tuple[np.ndarray, np.ndarray]]:
        """Split data chronologically into train/validation/test sets."""
        n = len(X)
        test_start = int(n * (1 - self.test_size))
        val_start = int(test_start * (1 - self.val_size))

        return {
            "train": (X[:val_start], y[:val_start]),
            "val": (X[val_start:test_start], y[val_start:test_start]),
            "test": (X[test_start:], y[test_start:]),
        }

    def _walk_forward_validation(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_type: str,
        custom_params: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Perform walk-forward (rolling-origin) validation.

        This simulates real-world usage where the model is trained on
        historical data and tested on future data, then the window
        rolls forward.
        """
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        fold_metrics: list[dict[str, float]] = []

        for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
            X_fold_train, X_fold_test = X[train_idx], X[test_idx]
            y_fold_train, y_fold_test = y[train_idx], y[test_idx]

            # Scale within each fold to prevent leakage
            if self.scale_features:
                fold_scaler = StandardScaler()
                X_fold_train = fold_scaler.fit_transform(X_fold_train)
                X_fold_test = fold_scaler.transform(X_fold_test)

            model = self._create_model(model_type, custom_params)
            model.fit(X_fold_train, y_fold_train)
            y_pred = model.predict(X_fold_test)

            fold_metric = {
                "fold": fold + 1,
                "train_size": len(train_idx),
                "test_size": len(test_idx),
                "accuracy": float(accuracy_score(y_fold_test, y_pred)),
                "f1_macro": float(f1_score(y_fold_test, y_pred, average="macro", zero_division=0)),
                "precision_macro": float(precision_score(y_fold_test, y_pred, average="macro", zero_division=0)),
                "recall_macro": float(recall_score(y_fold_test, y_pred, average="macro", zero_division=0)),
            }

            # Add AUC if binary or probabilities available
            if len(np.unique(y)) == 2:
                try:
                    y_proba = model.predict_proba(X_fold_test)[:, 1]
                    fold_metric["roc_auc"] = float(roc_auc_score(y_fold_test, y_proba))
                except (AttributeError, ValueError):
                    pass

            fold_metrics.append(fold_metric)
            logger.debug(
                f"  Fold {fold+1}: acc={fold_metric['accuracy']:.4f}, "
                f"f1={fold_metric['f1_macro']:.4f}"
            )

        # Aggregate results
        accuracies = [m["accuracy"] for m in fold_metrics]
        f1_scores = [m["f1_macro"] for m in fold_metrics]

        return {
            "n_folds": self.n_splits,
            "fold_metrics": fold_metrics,
            "mean_accuracy": float(np.mean(accuracies)),
            "std_accuracy": float(np.std(accuracies)),
            "mean_f1_macro": float(np.mean(f1_scores)),
            "std_f1_macro": float(np.std(f1_scores)),
            "min_accuracy": float(np.min(accuracies)),
            "max_accuracy": float(np.max(accuracies)),
        }

    def _create_model(
        self, model_type: str, custom_params: dict[str, Any] | None = None
    ) -> Any:
        """Create an ML model instance."""
        params = {**self.DEFAULT_PARAMS[model_type], **(custom_params or {})}

        if model_type == "logistic_regression":
            return LogisticRegression(**params)
        elif model_type == "random_forest":
            return RandomForestClassifier(**params)
        elif model_type == "gradient_boosting":
            return GradientBoostingClassifier(**params)
        elif model_type == "xgboost":
            return xgb.XGBClassifier(**params)
        elif model_type == "lightgbm":
            return lgb.LGBMClassifier(**params)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def _evaluate(
        self,
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray,
        class_map: dict[int, int],
    ) -> dict[str, float]:
        """Evaluate model on test set and return comprehensive metrics."""
        y_pred = model.predict(X_test)

        # Try to get probabilities
        y_proba = None
        try:
            y_proba = model.predict_proba(X_test)
        except (AttributeError, NotImplementedError):
            logger.warning("Model does not support probability predictions")

        metrics: dict[str, float] = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
            "f1_macro": float(f1_score(y_test, y_pred, average="macro", zero_division=0)),
            "f1_weighted": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
            "precision_macro": float(precision_score(y_test, y_pred, average="macro", zero_division=0)),
            "recall_macro": float(recall_score(y_test, y_pred, average="macro", zero_division=0)),
        }

        # Add probability-based metrics
        if y_proba is not None:
            try:
                if y_proba.shape[1] == 2:
                    metrics["roc_auc"] = float(roc_auc_score(y_test, y_proba[:, 1]))
                    metrics["log_loss"] = float(log_loss(y_test, y_proba))
                    metrics["average_precision"] = float(
                        average_precision_score(y_test, y_proba[:, 1])
                    )
                else:
                    metrics["roc_auc_ovr"] = float(
                        roc_auc_score(y_test, y_proba, multi_class="ovr", average="macro")
                    )
                    metrics["log_loss"] = float(log_loss(y_test, y_proba))
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not compute probability metrics: {e}")

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        metrics["confusion_matrix"] = cm.tolist()

        # Classification report
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        metrics["classification_report"] = report

        return metrics

    def _get_feature_importances(
        self, model: Any, feature_names: list[str]
    ) -> dict[str, float]:
        """Extract feature importances from the model."""
        importances: np.ndarray | None = None

        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            # For logistic regression, use mean absolute coefficient
            coef = np.abs(model.coef_)
            if coef.ndim > 1:
                importances = coef.mean(axis=0)
            else:
                importances = coef

        if importances is not None:
            # Normalize to sum to 1
            total = importances.sum()
            if total > 0:
                importances = importances / total
            return {
                name: float(imp) for name, imp in zip(feature_names, importances)
            }

        return {}

    def _get_model_params(self, model: Any, model_type: str) -> dict[str, Any]:
        """Extract model parameters for serialization."""
        if hasattr(model, "get_params"):
            params = model.get_params()
            # Convert numpy types to Python types for JSON serialization
            return {k: (v.item() if hasattr(v, "item") else v) for k, v in params.items()}
        return {"model_type": model_type}

    def _generate_version(self, model_name: str) -> str:
        """Generate a version string based on existing models."""
        existing = list(self.model_dir.glob(f"{model_name}_v*.joblib"))
        if not existing:
            return "1.0.0"

        versions = []
        for f in existing:
            try:
                ver_str = f.stem.split("_v")[-1]
                versions.append(tuple(int(x) for x in ver_str.split(".")))
            except (ValueError, IndexError):
                continue

        if not versions:
            return "1.0.0"

        latest = max(versions)
        return f"{latest[0]}.{latest[1]}.{latest[2] + 1}"

    def _save_model(self, model: Any, model_info: ModelInfo) -> Path:
        """Save model and metadata to disk."""
        self.model_dir.mkdir(parents=True, exist_ok=True)

        model_path = self.model_dir / f"{model_info.name}_v{model_info.version}_{model_info.model_id}.joblib"
        metadata_path = self.model_dir / f"{model_info.name}_v{model_info.version}_{model_info.model_id}.json"

        # Save model with scaler
        artifact = {
            "model": model,
            "scaler": self.scaler,
            "model_info": model_info,
        }
        joblib.dump(artifact, model_path)

        # Save metadata as JSON
        with open(metadata_path, "w") as f:
            f.write(model_info.to_json())

        logger.info(f"Model saved to: {model_path}")
        logger.info(f"Metadata saved to: {metadata_path}")

        return model_path

    def load_model(self, model_path: str | Path) -> tuple[Any, ModelInfo, StandardScaler | None]:
        """Load a saved model from disk.

        Returns:
            Tuple of (model, model_info, scaler)
        """
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        artifact = joblib.load(model_path)
        model = artifact["model"]
        scaler = artifact.get("scaler")
        model_info = artifact["model_info"]

        logger.info(f"Loaded model: {model_info.name} v{model_info.version} (ID: {model_info.model_id})")

        return model, model_info, scaler

    @property
    def model(self) -> Any:
        """Get the trained model."""
        return self._model

    @property
    def model_info(self) -> ModelInfo | None:
        """Get the model info."""
        return self._model_info
