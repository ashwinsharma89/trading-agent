"""
Ratio Engine — core calculation logic.
All inputs/outputs are pandas Series/DataFrames.
"""
from __future__ import annotations

import logging
from typing import Literal

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def calculate_ratio(
    series_a: pd.Series,
    series_b: pd.Series,
    method: str = "divide",
) -> pd.Series:
    """
    Align both series on common dates and return series_a / series_b.
    Forward-fill the shorter series (e.g. monthly M2 vs daily index).
    """
    # Combine into DataFrame on their union index, then forward-fill gaps
    df = pd.DataFrame({"a": series_a, "b": series_b})
    df = df.sort_index().ffill()
    df = df.dropna()

    if df.empty:
        return pd.Series(dtype=float)

    ratio = df["a"] / df["b"]
    ratio.name = "ratio"
    return ratio


def calculate_zscore(series: pd.Series, window: int = 52) -> pd.Series:
    """
    Rolling z-score with the given window.
    window unit matches the series frequency (e.g. 52 weeks ≈ 1 year for weekly data,
    or 252 days ≈ 1 year for daily data).
    """
    rolling_mean = series.rolling(window=window, min_periods=max(5, window // 4)).mean()
    rolling_std  = series.rolling(window=window, min_periods=max(5, window // 4)).std()
    zscore = (series - rolling_mean) / rolling_std
    zscore.name = "zscore"
    return zscore


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Wilder's RSI."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    rsi.name = "rsi"
    return rsi


def detect_extremes(
    zscore: pd.Series,
    upper_threshold: float = 2.0,
    lower_threshold: float = -2.0,
) -> dict:
    """
    Determine signal based on latest z-score value.
    Returns {"signal": "overbought"|"oversold"|"neutral", "current_zscore": float}
    """
    current = float(zscore.dropna().iloc[-1]) if not zscore.dropna().empty else 0.0

    if current >= upper_threshold:
        signal = "overbought"
    elif current <= lower_threshold:
        signal = "oversold"
    else:
        signal = "neutral"

    return {"signal": signal, "current_zscore": round(current, 4)}


def _pct_change(series: pd.Series, periods: int) -> float | None:
    """Percentage change over last `periods` bars."""
    clean = series.dropna()
    if len(clean) <= periods:
        return None
    old = float(clean.iloc[-periods - 1])
    new = float(clean.iloc[-1])
    if old == 0:
        return None
    return round((new - old) / old * 100, 2)


def _series_to_chart_points(series: pd.Series) -> list[dict]:
    """Convert pandas Series to [{"time": "YYYY-MM-DD", "value": float}]."""
    points = []
    for dt, val in series.dropna().items():
        if isinstance(dt, pd.Timestamp):
            time_str = dt.strftime("%Y-%m-%d")
        else:
            time_str = str(dt)[:10]
        fval = float(val)
        if not (np.isfinite(fval)):
            continue
        points.append({"time": time_str, "value": round(fval, 6)})
    return points


def get_ratio_chart_data(
    series_a: pd.Series,
    series_b: pd.Series,
    zscore_window: int = 52,
) -> dict:
    """
    Build full chart payload.

    zscore_window is in the natural frequency of the ratio series.
    For daily data, pass 252 (1 year). For weekly, pass 52.
    """
    ratio = calculate_ratio(series_a, series_b)
    if ratio.empty:
        return {
            "ratio": [], "zscore": [], "rsi": [],
            "signal": "neutral", "current_value": 0,
            "current_zscore": 0, "pct_change_1w": None,
            "pct_change_1m": None, "pct_change_3m": None,
        }

    # Infer frequency: if median gap > 3 days → weekly/monthly → window = 52
    median_gap = ratio.index.to_series().diff().median()
    if pd.isna(median_gap):
        window = zscore_window
    elif median_gap.days <= 1:
        window = 252   # ~1 year of daily data
    elif median_gap.days <= 8:
        window = 52    # ~1 year of weekly data
    else:
        window = 12    # monthly → 12 months

    zscore = calculate_zscore(ratio, window=window)
    rsi    = calculate_rsi(ratio, period=14)
    extreme = detect_extremes(zscore)

    current_value = round(float(ratio.dropna().iloc[-1]), 6) if not ratio.dropna().empty else 0.0

    return {
        "ratio":   _series_to_chart_points(ratio),
        "zscore":  _series_to_chart_points(zscore),
        "rsi":     _series_to_chart_points(rsi),
        "signal":  extreme["signal"],
        "current_value":  current_value,
        "current_zscore": extreme["current_zscore"],
        "pct_change_1w":  _pct_change(ratio, 5),
        "pct_change_1m":  _pct_change(ratio, 21),
        "pct_change_3m":  _pct_change(ratio, 63),
    }
