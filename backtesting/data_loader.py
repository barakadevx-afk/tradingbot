"""
BARAKA AI - Data Loader
=======================

Loads and validates historical market data for backtesting.
Ensures proper chronological ordering and data quality.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class DataConfig:
    """Configuration for data loading."""

    symbol: str = "BTCUSDT"
    timeframe: str = "1h"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    data_path: Optional[Union[str, Path]] = None
    required_columns: list[str] = field(
        default_factory=lambda: ["open", "high", "low", "close", "volume"]
    )
    timestamp_column: str = "timestamp"
    drop_na: bool = True
    validate_ohlc: bool = True


class DataLoader:
    """Loads historical market data with proper chronological ordering."""

    SUPPORTED_TIMEFRAMES = {
        "1m", "3m", "5m", "15m", "30m",
        "1h", "2h", "4h", "6h", "8h", "12h",
        "1d", "3d", "1w", "1M",
    }

    def __init__(self, config: Optional[DataConfig] = None):
        self.config = config or DataConfig()
        self._data: Optional[pd.DataFrame] = None

    @property
    def data(self) -> pd.DataFrame:
        """Return the loaded data."""
        if self._data is None:
            raise ValueError("No data loaded. Call load() first.")
        return self._data

    def load(self, source: Optional[Union[str, Path, pd.DataFrame]] = None) -> pd.DataFrame:
        """
        Load data from a file path, DataFrame, or configured source.

        Parameters
        ----------
        source : str, Path, pd.DataFrame, or None
            If None, uses config.data_path. If DataFrame, uses directly.

        Returns
        -------
        pd.DataFrame
            Chronologically ordered OHLCV data.
        """
        if isinstance(source, pd.DataFrame):
            df = source.copy()
        elif source is not None:
            df = self._load_from_file(source)
        elif self.config.data_path is not None:
            df = self._load_from_file(self.config.data_path)
        else:
            raise ValueError(
                "No data source provided. Pass a file path, DataFrame, "
                "or set config.data_path."
            )

        df = self._standardize_columns(df)
        df = self._ensure_datetime_index(df)
        df = self._sort_chronologically(df)
        df = self._filter_date_range(df)

        if self.config.drop_na:
            initial_len = len(df)
            df = df.dropna(subset=self.config.required_columns)
            dropped = initial_len - len(df)
            if dropped > 0:
                logger.warning("Dropped %d rows with NaN values", dropped)

        if self.config.validate_ohlc:
            df = self._validate_ohlc(df)

        self._data = df
        logger.info(
            "Loaded %d rows for %s [%s] from %s to %s",
            len(df),
            self.config.symbol,
            self.config.timeframe,
            df.index[0],
            df.index[-1],
        )
        return df

    def _load_from_file(self, path: Union[str, Path]) -> pd.DataFrame:
        """Load data from CSV, Parquet, or Feather file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")

        suffix = path.suffix.lower()
        if suffix == ".csv":
            df = pd.read_csv(path)
        elif suffix in (".parquet", ".pq"):
            df = pd.read_parquet(path)
        elif suffix in (".feather", ".ftr"):
            df = pd.read_feather(path)
        elif suffix in (".json",):
            df = pd.read_json(path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

        logger.info("Loaded %d rows from %s", len(df), path)
        return df

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to lowercase."""
        df = df.copy()
        df.columns = [c.lower().strip() for c in df.columns]

        # Map common alternative names
        column_map = {
            "time": "timestamp",
            "date": "timestamp",
            "datetime": "timestamp",
            "o": "open",
            "h": "high",
            "l": "low",
            "c": "close",
            "v": "volume",
            "vol": "volume",
            "adj close": "adj_close",
        }
        df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})
        return df

    def _ensure_datetime_index(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure the DataFrame has a DatetimeIndex."""
        df = df.copy()

        if isinstance(df.index, pd.DatetimeIndex):
            return df

        if self.config.timestamp_column in df.columns:
            ts_col = self.config.timestamp_column
            # Try parsing as datetime
            if not pd.api.types.is_datetime64_any_dtype(df[ts_col]):
                # Try numeric (unix timestamp in seconds or milliseconds)
                sample = df[ts_col].iloc[0]
                if isinstance(sample, (int, float, np.integer, np.floating)):
                    if sample > 1e12:
                        df[ts_col] = pd.to_datetime(df[ts_col], unit="ms")
                    else:
                        df[ts_col] = pd.to_datetime(df[ts_col], unit="s")
                else:
                    df[ts_col] = pd.to_datetime(df[ts_col])
            df = df.set_index(ts_col)
        else:
            # Try to find any datetime column
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df = df.set_index(col)
                    break
            else:
                raise ValueError(
                    f"No timestamp column found. Expected '{self.config.timestamp_column}' "
                    "or a datetime column."
                )

        df.index = pd.DatetimeIndex(df.index)
        df.index.name = "timestamp"
        return df

    def _sort_chronologically(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sort data in chronological order."""
        if not df.index.is_monotonic_increasing:
            logger.warning("Data was not in chronological order. Sorting...")
            df = df.sort_index()
        return df

    def _filter_date_range(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter data to the configured date range."""
        if self.config.start_date is not None:
            start = pd.Timestamp(self.config.start_date)
            df = df[df.index >= start]
        if self.config.end_date is not None:
            end = pd.Timestamp(self.config.end_date)
            df = df[df.index <= end]
        return df

    def _validate_ohlc(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate OHLC relationships and remove invalid rows."""
        initial_len = len(df)

        # High must be >= Low
        invalid_hl = df["high"] < df["low"]
        # High must be >= Open and Close
        invalid_ho = df["high"] < df["open"]
        invalid_hc = df["high"] < df["close"]
        # Low must be <= Open and Close
        invalid_lo = df["low"] > df["open"]
        invalid_lc = df["low"] > df["close"]

        invalid_mask = invalid_hl | invalid_ho | invalid_hc | invalid_lo | invalid_lc
        n_invalid = invalid_mask.sum()

        if n_invalid > 0:
            logger.warning(
                "Removing %d rows with invalid OHLC relationships", n_invalid
            )
            df = df[~invalid_mask]

        # Check for zero/negative prices
        price_cols = ["open", "high", "low", "close"]
        for col in price_cols:
            non_positive = df[col] <= 0
            if non_positive.any():
                logger.warning(
                    "Removing %d rows with non-positive %s", non_positive.sum(), col
                )
                df = df[~non_positive]

        total_dropped = initial_len - len(df)
        if total_dropped > 0:
            logger.info("Total rows dropped during validation: %d", total_dropped)

        return df

    def get_data_summary(self) -> dict:
        """Return a summary of the loaded data."""
        if self._data is None:
            raise ValueError("No data loaded. Call load() first.")

        df = self._data
        return {
            "symbol": self.config.symbol,
            "timeframe": self.config.timeframe,
            "rows": len(df),
            "start_date": str(df.index[0]),
            "end_date": str(df.index[-1]),
            "duration_days": (df.index[-1] - df.index[0]).days,
            "columns": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "price_range": {
                "min_low": float(df["low"].min()),
                "max_high": float(df["high"].max()),
            },
        }

    def resample(self, timeframe: str) -> pd.DataFrame:
        """Resample data to a different timeframe."""
        if self._data is None:
            raise ValueError("No data loaded. Call load() first.")

        if timeframe not in self.SUPPORTED_TIMEFRAMES:
            raise ValueError(
                f"Unsupported timeframe: {timeframe}. "
                f"Supported: {self.SUPPORTED_TIMEFRAMES}"
            )

        resampled = self._data.resample(timeframe).agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        ).dropna()

        return resampled
