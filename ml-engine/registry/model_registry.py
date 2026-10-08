"""
Model Registry
==============
Central registry for managing ML model lifecycle.

Statuses:
- DRAFT: Newly trained, not yet evaluated
- TESTING: Under evaluation (backtesting, paper trading)
- APPROVED: Passed evaluation, ready for live trading
- PRODUCTION: Actively used in live trading
- RETIRED: No longer in use

Only APPROVED and PRODUCTION models can be used for live trading.

Admin capabilities:
- View all models and their status
- Compare models side-by-side
- Approve models (TESTING -> APPROVED)
- Retire models (any -> RETIRED)
- View detailed metrics
- View drift reports
- Inspect version history
"""

from __future__ import annotations

import json
import logging
import pickle
import shutil
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from ml_engine.training.trainer import ModelInfo

logger = logging.getLogger(__name__)


class ModelStatus(Enum):
    """Model lifecycle statuses."""

    DRAFT = "draft"
    TESTING = "testing"
    APPROVED = "approved"
    PRODUCTION = "production"
    RETIRED = "retired"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "ModelStatus":
        """Create ModelStatus from string."""
        for status in cls:
            if status.value == value.lower():
                return status
        raise ValueError(f"Unknown model status: {value}")


@dataclass
class RegistryEntry:
    """Entry in the model registry."""

    model_id: str
    name: str
    version: str
    status: ModelStatus
    model_type: str
    strategy: str
    created_at: str
    updated_at: str
    model_path: str
    metadata_path: str
    metrics: dict[str, Any] = field(default_factory=dict)
    parameters: dict[str, Any] = field(default_factory=dict)
    features: list[str] = field(default_factory=list)
    training_date: str = ""
    dataset_period: dict[str, str] = field(default_factory=dict)
    dataset_size: int = 0
    approved_by: str = ""
    approved_at: str = ""
    retired_at: str = ""
    retirement_reason: str = ""
    notes: str = ""
    tags: list[str] = field(default_factory=list)
    parent_model_id: str = ""  # For version lineage

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RegistryEntry":
        data = dict(data)
        data["status"] = ModelStatus.from_string(data["status"])
        return cls(**data)

    def load_model(self) -> Any:
        """Load the serialized model from disk."""
        model_path = Path(self.model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        artifact = joblib.load(model_path)
        if isinstance(artifact, dict) and "model" in artifact:
            return artifact["model"]
        return artifact

    def load_full_artifact(self) -> dict[str, Any]:
        """Load the full artifact (model + scaler + info)."""
        model_path = Path(self.model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        return joblib.load(model_path)

    @property
    def is_live_ready(self) -> bool:
        """Check if model is approved for live trading."""
        return self.status in (ModelStatus.APPROVED, ModelStatus.PRODUCTION)

    @property
    def is_active(self) -> bool:
        """Check if model is currently active (not retired)."""
        return self.status != ModelStatus.RETIRED


class ModelRegistry:
    """Central registry for ML model lifecycle management.

    Manages model artifacts, metadata, and status transitions.
    Thread-safe for single-process usage.
    """

    VALID_TRANSITIONS: dict[ModelStatus, set[ModelStatus]] = {
        ModelStatus.DRAFT: {ModelStatus.TESTING, ModelStatus.RETIRED},
        ModelStatus.TESTING: {ModelStatus.APPROVED, ModelStatus.DRAFT, ModelStatus.RETIRED},
        ModelStatus.APPROVED: {ModelStatus.PRODUCTION, ModelStatus.TESTING, ModelStatus.RETIRED},
        ModelStatus.PRODUCTION: {ModelStatus.RETIRED, ModelStatus.TESTING},
        ModelStatus.RETIRED: set(),  # Terminal state
    }

    def __init__(self, storage_path: str | Path = "models/registry"):
        """Initialize the model registry.

        Args:
            storage_path: Directory to store registry data and model artifacts.
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.registry_file = self.storage_path / "registry.json"
        self.models_dir = self.storage_path / "models"
        self.models_dir.mkdir(exist_ok=True)

        self._entries: dict[str, RegistryEntry] = {}
        self._load_registry()

        logger.info(f"Model registry initialized at: {self.storage_path}")

    def register(
        self,
        model: Any,
        model_info: ModelInfo,
        status: ModelStatus = ModelStatus.DRAFT,
        strategy: str = "default",
        tags: list[str] | None = None,
        notes: str = "",
        parent_model_id: str = "",
    ) -> RegistryEntry:
        """Register a new model in the registry.

        Args:
            model: Trained model object.
            model_info: Model metadata.
            status: Initial status (default: DRAFT).
            strategy: Strategy association.
            tags: Optional tags for categorization.
            notes: Additional notes.
            parent_model_id: ID of parent model (for versioning).

        Returns:
            The created RegistryEntry.
        """
        model_id = model_info.model_id or str(uuid.uuid4())[:8]
        version = model_info.version

        # Create model directory
        model_dir = self.models_dir / f"{model_info.name}_v{version}_{model_id}"
        model_dir.mkdir(exist_ok=True)

        # Save model artifact
        model_path = model_dir / "model.joblib"
        artifact = {
            "model": model,
            "model_info": model_info,
        }
        joblib.dump(artifact, model_path)

        # Save metadata
        metadata_path = model_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(model_info.to_dict(), f, indent=2, default=str)

        now = datetime.now(timezone.utc).isoformat()

        entry = RegistryEntry(
            model_id=model_id,
            name=model_info.name,
            version=version,
            status=status,
            model_type=model_info.model_type,
            strategy=strategy or model_info.strategy,
            created_at=now,
            updated_at=now,
            model_path=str(model_path),
            metadata_path=str(metadata_path),
            metrics=model_info.metrics,
            parameters=model_info.parameters,
            features=model_info.features,
            training_date=model_info.training_date,
            dataset_period=model_info.dataset_period,
            dataset_size=model_info.dataset_size,
            notes=notes or model_info.notes,
            tags=tags or [],
            parent_model_id=parent_model_id,
        )

        self._entries[model_id] = entry
        self._save_registry()

        logger.info(f"Registered model: {model_info.name} v{version} (ID: {model_id}, Status: {status.value})")
        return entry

    def get(self, model_id: str) -> RegistryEntry | None:
        """Get a registry entry by model ID."""
        return self._entries.get(model_id)

    def get_by_name_version(self, name: str, version: str) -> RegistryEntry | None:
        """Get a registry entry by name and version."""
        for entry in self._entries.values():
            if entry.name == name and entry.version == version:
                return entry
        return None

    def list_all(
        self,
        status: ModelStatus | None = None,
        model_type: str | None = None,
        strategy: str | None = None,
    ) -> list[RegistryEntry]:
        """List all registry entries with optional filtering.

        Args:
            status: Filter by status.
            model_type: Filter by model type.
            strategy: Filter by strategy.

        Returns:
            List of matching RegistryEntry objects.
        """
        entries = list(self._entries.values())

        if status is not None:
            entries = [e for e in entries if e.status == status]
        if model_type is not None:
            entries = [e for e in entries if e.model_type == model_type]
        if strategy is not None:
            entries = [e for e in entries if e.strategy == strategy]

        return sorted(entries, key=lambda e: e.created_at, reverse=True)

    def list_live_ready(self) -> list[RegistryEntry]:
        """List all models ready for live trading (APPROVED or PRODUCTION)."""
        return [
            e for e in self._entries.values()
            if e.status in (ModelStatus.APPROVED, ModelStatus.PRODUCTION)
        ]

    def update_status(
        self,
        model_id: str,
        new_status: ModelStatus,
        updated_by: str = "system",
        reason: str = "",
    ) -> RegistryEntry:
        """Update the status of a model.

        Args:
            model_id: ID of the model to update.
            new_status: New status to set.
            updated_by: Who/what initiated the change.
            reason: Reason for the status change.

        Returns:
            Updated RegistryEntry.

        Raises:
            ValueError: If the status transition is invalid.
        """
        entry = self._entries.get(model_id)
        if entry is None:
            raise ValueError(f"Model '{model_id}' not found in registry.")

        # Validate transition
        if new_status not in self.VALID_TRANSITIONS.get(entry.status, set()):
            raise ValueError(
                f"Invalid status transition: {entry.status.value} -> {new_status.value}. "
                f"Valid transitions from {entry.status.value}: "
                f"{[s.value for s in self.VALID_TRANSITIONS.get(entry.status, set())]}"
            )

        old_status = entry.status
        entry.status = new_status
        entry.updated_at = datetime.now(timezone.utc).isoformat()

        # Record approval/retirement details
        if new_status == ModelStatus.APPROVED:
            entry.approved_by = updated_by
            entry.approved_at = entry.updated_at
        elif new_status == ModelStatus.RETIRED:
            entry.retired_at = entry.updated_at
            entry.retirement_reason = reason

        self._save_registry()

        logger.info(
            f"Model '{model_id}' status changed: {old_status.value} -> {new_status.value} "
            f"(by: {updated_by})"
        )
        return entry

    def approve(
        self, model_id: str, approved_by: str = "admin"
    ) -> RegistryEntry:
        """Approve a model for live trading.

        Args:
            model_id: ID of the model to approve.
            approved_by: Who is approving the model.

        Returns:
            Updated RegistryEntry.
        """
        return self.update_status(
            model_id, ModelStatus.APPROVED, updated_by=approved_by
        )

    def promote_to_production(
        self, model_id: str, updated_by: str = "admin"
    ) -> RegistryEntry:
        """Promote an approved model to production.

        Args:
            model_id: ID of the model to promote.
            updated_by: Who is promoting the model.

        Returns:
            Updated RegistryEntry.
        """
        return self.update_status(
            model_id, ModelStatus.PRODUCTION, updated_by=updated_by
        )

    def retire(
        self,
        model_id: str,
        reason: str = "",
        updated_by: str = "admin",
    ) -> RegistryEntry:
        """Retire a model.

        Args:
            model_id: ID of the model to retire.
            reason: Reason for retirement.
            updated_by: Who is retiring the model.

        Returns:
            Updated RegistryEntry.
        """
        return self.update_status(
            model_id,
            ModelStatus.RETIRED,
            updated_by=updated_by,
            reason=reason,
        )

    def compare_models(self, model_ids: list[str]) -> dict[str, Any]:
        """Compare multiple models side-by-side.

        Args:
            model_ids: List of model IDs to compare.

        Returns:
            Comparison dictionary with metrics and metadata.
        """
        entries = []
        for mid in model_ids:
            entry = self._entries.get(mid)
            if entry is None:
                raise ValueError(f"Model '{mid}' not found in registry.")
            entries.append(entry)

        comparison: dict[str, Any] = {
            "models": [],
            "metrics_comparison": {},
            "recommendation": "",
        }

        # Collect metrics for comparison
        all_metrics: dict[str, list[float]] = {}
        for entry in entries:
            model_summary = {
                "model_id": entry.model_id,
                "name": entry.name,
                "version": entry.version,
                "status": entry.status.value,
                "model_type": entry.model_type,
                "strategy": entry.strategy,
                "training_date": entry.training_date,
                "dataset_size": entry.dataset_size,
                "metrics": entry.metrics,
            }
            comparison["models"].append(model_summary)

            for metric_name, value in entry.metrics.items():
                if isinstance(value, (int, float)):
                    all_metrics.setdefault(metric_name, []).append(float(value))

        # Find best model for each metric
        best_metrics = {}
        for metric_name, values in all_metrics.items():
            if values:
                best_idx = np.argmax(values)
                best_metrics[metric_name] = {
                    "best_value": values[best_idx],
                    "best_model_id": entries[best_idx].model_id,
                    "all_values": values,
                }

        comparison["metrics_comparison"] = best_metrics

        # Generate recommendation
        if entries:
            # Prefer live-ready models with best accuracy
            live_ready = [e for e in entries if e.is_live_ready]
            if live_ready:
                best = max(
                    live_ready,
                    key=lambda e: e.metrics.get("accuracy", 0),
                )
                comparison["recommendation"] = (
                    f"Recommended: {best.name} v{best.version} "
                    f"(ID: {best.model_id}, Accuracy: {best.metrics.get('accuracy', 0):.4f})"
                )
            else:
                best = max(entries, key=lambda e: e.metrics.get("accuracy", 0))
                comparison["recommendation"] = (
                    f"Best performing (not live-ready): {best.name} v{best.version} "
                    f"(ID: {best.model_id}, Status: {best.status.value})"
                )

        return comparison

    def get_version_history(self, name: str) -> list[RegistryEntry]:
        """Get version history for a model name.

        Args:
            name: Model name to look up.

        Returns:
            List of RegistryEntry objects sorted by version.
        """
        entries = [e for e in self._entries.values() if e.name == name]
        return sorted(entries, key=lambda e: e.version)

    def get_drift_report(self, model_id: str) -> dict[str, Any]:
        """Get drift report for a model.

        Args:
            model_id: ID of the model.

        Returns:
            Drift report dictionary.
        """
        entry = self._entries.get(model_id)
        if entry is None:
            raise ValueError(f"Model '{model_id}' not found in registry.")

        # Load full metrics from metadata
        try:
            with open(entry.metadata_path, "r") as f:
                full_metadata = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            full_metadata = {}

        walk_forward = full_metadata.get("walk_forward_results", {})

        return {
            "model_id": model_id,
            "name": entry.name,
            "version": entry.version,
            "status": entry.status.value,
            "training_date": entry.training_date,
            "current_metrics": entry.metrics,
            "walk_forward_summary": {
                "mean_accuracy": walk_forward.get("mean_accuracy", 0),
                "std_accuracy": walk_forward.get("std_accuracy", 0),
                "mean_f1": walk_forward.get("mean_f1_macro", 0),
                "n_folds": walk_forward.get("n_folds", 0),
            },
            "dataset_period": entry.dataset_period,
            "dataset_size": entry.dataset_size,
            "last_updated": entry.updated_at,
            "drift_indicators": {
                "accuracy_trend": "stable",  # Would be computed from monitoring data
                "data_freshness_days": self._calculate_data_freshness(entry.training_date),
            },
        }

    def delete(self, model_id: str, force: bool = False) -> None:
        """Delete a model from the registry.

        Args:
            model_id: ID of the model to delete.
            force: If True, delete even if model is PRODUCTION.
        """
        entry = self._entries.get(model_id)
        if entry is None:
            raise ValueError(f"Model '{model_id}' not found in registry.")

        if entry.status == ModelStatus.PRODUCTION and not force:
            raise ValueError(
                f"Cannot delete PRODUCTION model '{model_id}'. "
                "Retire it first or use force=True."
            )

        # Remove files
        model_dir = Path(entry.model_path).parent
        if model_dir.exists():
            shutil.rmtree(model_dir)

        # Remove from registry
        del self._entries[model_id]
        self._save_registry()

        logger.info(f"Deleted model: {model_id}")

    def get_statistics(self) -> dict[str, Any]:
        """Get registry statistics."""
        total = len(self._entries)
        by_status = {}
        by_type = {}
        by_strategy = {}

        for entry in self._entries.values():
            status = entry.status.value
            by_status[status] = by_status.get(status, 0) + 1

            mtype = entry.model_type
            by_type[mtype] = by_type.get(mtype, 0) + 1

            strat = entry.strategy
            by_strategy[strat] = by_strategy.get(strat, 0) + 1

        live_ready = len(self.list_live_ready())

        return {
            "total_models": total,
            "live_ready_models": live_ready,
            "by_status": by_status,
            "by_type": by_type,
            "by_strategy": by_strategy,
            "storage_path": str(self.storage_path),
        }

    def _save_registry(self) -> None:
        """Persist registry to disk."""
        data = {
            "version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "entries": {mid: entry.to_dict() for mid, entry in self._entries.items()},
        }

        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _load_registry(self) -> None:
        """Load registry from disk."""
        if not self.registry_file.exists():
            logger.info("No existing registry found. Starting fresh.")
            return

        try:
            with open(self.registry_file, "r") as f:
                data = json.load(f)

            for model_id, entry_data in data.get("entries", {}).items():
                try:
                    entry = RegistryEntry.from_dict(entry_data)
                    self._entries[model_id] = entry
                except (ValueError, KeyError) as e:
                    logger.warning(f"Failed to load registry entry '{model_id}': {e}")

            logger.info(f"Loaded {len(self._entries)} models from registry.")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load registry: {e}. Starting fresh.")
            self._entries = {}

    @staticmethod
    def _calculate_data_freshness(training_date: str) -> int:
        """Calculate days since training."""
        try:
            train_date = datetime.fromisoformat(training_date.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            return (now - train_date).days
        except (ValueError, TypeError):
            return -1
