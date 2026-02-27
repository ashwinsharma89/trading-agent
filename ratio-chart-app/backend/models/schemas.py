"""
Pydantic schemas for the Financial Ratio Chart App
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


# ── Asset & Source ────────────────────────────────────────────────────────────

class AssetSpec(BaseModel):
    source: Literal["zerodha", "upstox", "twelve_data", "fred"]
    key: str  # e.g. "NSE:NIFTY 50", "XAU/USD", "M2SL"
    label: Optional[str] = None  # human-readable name


# ── Ratio calculation ─────────────────────────────────────────────────────────

class RatioCalculateRequest(BaseModel):
    asset_a: AssetSpec
    asset_b: AssetSpec
    timeframe: Literal["1M", "3M", "6M", "1Y", "3Y", "5Y"] = "1Y"


class ChartPoint(BaseModel):
    time: str  # ISO date string "YYYY-MM-DD"
    value: float


class RatioChartData(BaseModel):
    ratio: List[ChartPoint]
    zscore: List[ChartPoint]
    rsi: List[ChartPoint]
    signal: Literal["overbought", "oversold", "neutral"]
    current_value: float
    current_zscore: float
    pct_change_1w: Optional[float] = None
    pct_change_1m: Optional[float] = None
    pct_change_3m: Optional[float] = None
    asset_a_label: str
    asset_b_label: str
    note: Optional[str] = None  # e.g. "M2 interpolated (monthly)"


# ── Watchlist ─────────────────────────────────────────────────────────────────

class WatchlistItem(BaseModel):
    id: Optional[int] = None
    name: str
    asset_a: AssetSpec
    asset_b: AssetSpec
    created_at: Optional[datetime] = None
    # Latest computed values (populated on fetch)
    current_value: Optional[float] = None
    current_zscore: Optional[float] = None
    signal: Optional[str] = None
    pct_change_1w: Optional[float] = None


class WatchlistCreateRequest(BaseModel):
    name: str
    asset_a: AssetSpec
    asset_b: AssetSpec


# ── Alerts ────────────────────────────────────────────────────────────────────

class AlertCreateRequest(BaseModel):
    name: str
    asset_a: AssetSpec
    asset_b: AssetSpec
    condition: Literal["zscore_above", "zscore_below", "ratio_above", "ratio_below"]
    threshold: float
    notify_via: Literal["ui"] = "ui"


class Alert(BaseModel):
    id: Optional[int] = None
    name: str
    asset_a: AssetSpec
    asset_b: AssetSpec
    condition: str
    threshold: float
    notify_via: str = "ui"
    is_active: bool = True
    triggered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


# ── Instrument search ─────────────────────────────────────────────────────────

class InstrumentResult(BaseModel):
    key: str           # instrument key to use in API calls
    label: str         # human-readable name
    source: str        # "zerodha" | "upstox" | "twelve_data" | "fred"
    exchange: Optional[str] = None
    instrument_type: Optional[str] = None


# ── OHLCV ─────────────────────────────────────────────────────────────────────

class OHLCVPoint(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[float] = None
