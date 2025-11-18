"""Utility for fetching live commodity data and derived signals."""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from typing import Dict, List

import pandas as pd
import yfinance as yf

# Default futures/spot tickers available on Yahoo Finance
COMMODITY_TICKERS: Dict[str, str] = {
    "Brent Crude": "BZ=F",
    "WTI Crude": "CL=F",
    "Henry Hub Gas": "NG=F",
    "LME Copper": "HG=F",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Corn": "ZC=F",
    "Soybeans": "ZS=F",
    "Palm Oil": "FCPO.MY",
    "EU Carbon": "C02=F"
}


TAILWIND_THRESHOLDS = {
    "Brent Crude": {"upper": 95, "lower": 75},
    "WTI Crude": {"upper": 90, "lower": 70},
    "Henry Hub Gas": {"upper": 4.5, "lower": 2.5},
    "LME Copper": {"upper": 9500, "lower": 7800},
    "Gold": {"upper": 2250, "lower": 1900},
    "Corn": {"upper": 6, "lower": 4},
    "Soybeans": {"upper": 14, "lower": 11.5},
    "EU Carbon": {"upper": 100, "lower": 70}
}


@dataclass
class CommoditySnapshot:
    name: str
    price: float
    change_pct: float
    trend: str
    status: str
    updated_at: _dt.datetime


def _determine_trend(series: pd.Series) -> str:
    if series.empty:
        return "UNKNOWN"
    ma_short = series.rolling(window=20).mean().iloc[-1]
    ma_long = series.rolling(window=60).mean().iloc[-1]
    if pd.isna(ma_short) or pd.isna(ma_long):
        return "UNKNOWN"
    if ma_short > ma_long:
        return "UP"
    if ma_short < ma_long:
        return "DOWN"
    return "FLAT"


def _classify_status(name: str, price: float) -> str:
    thresholds = TAILWIND_THRESHOLDS.get(name)
    if not thresholds:
        return "NEUTRAL"
    if price >= thresholds.get("upper", float("inf")):
        return "ELEVATED"
    if price <= thresholds.get("lower", float("-inf")):
        return "DEPRESSED"
    return "RANGE"


def fetch_commodity_snapshot(tickers: Dict[str, str] | None = None) -> Dict[str, CommoditySnapshot]:
    """Fetch price/Delta/trend for configured commodities."""
    mapping = tickers or COMMODITY_TICKERS
    snapshots: Dict[str, CommoditySnapshot] = {}

    for name, ticker in mapping.items():
        try:
            data = yf.Ticker(ticker).history(period="3mo", interval="1d")
            if data.empty:
                continue
            latest = data.iloc[-1]
            prev = data.iloc[-2] if len(data) > 1 else latest
            change_pct = (latest["Close"] / prev["Close"] - 1) * 100 if prev["Close"] else 0
            trend = _determine_trend(data["Close"])
            status = _classify_status(name, float(latest["Close"]))
            snapshots[name] = CommoditySnapshot(
                name=name,
                price=float(latest["Close"]),
                change_pct=float(change_pct),
                trend=trend,
                status=status,
                updated_at=_dt.datetime.utcnow()
            )
        except Exception as exc:  # pragma: no cover - network calls
            snapshots[name] = CommoditySnapshot(
                name=name,
                price=float("nan"),
                change_pct=0.0,
                trend="UNKNOWN",
                status=f"ERROR: {exc}",
                updated_at=_dt.datetime.utcnow()
            )

    return snapshots


SECTOR_COMMODITY_MAP: Dict[str, List[str]] = {
    "Energy": ["Brent Crude", "WTI Crude", "Henry Hub Gas"],
    "Airlines": ["Brent Crude"],
    "Automobile & Auto Components": ["Brent Crude", "LME Copper", "Aluminum"],
    "Metals & Mining": ["LME Copper"],
    "Chemicals & Fertilizers": ["WTI Crude", "Henry Hub Gas"],
    "FMCG": ["Corn", "Soybeans", "Palm Oil", "Cocoa"],
    "Utilities": ["Henry Hub Gas", "EU Carbon"],
    "Capital Goods": ["LME Copper", "EU Carbon"],
    "Renewable Energy": ["LME Copper", "EU Carbon"],
}


def evaluate_sector_pressure(sector: str, snapshots: Dict[str, CommoditySnapshot]) -> Dict[str, str]:
    """Return simple tailwind/headwind signals for a sector based on linked commodities."""
    linked = SECTOR_COMMODITY_MAP.get(sector, [])
    impact: Dict[str, str] = {}
    for name in linked:
        snap = snapshots.get(name)
        if not snap:
            continue
        if snap.status == "ELEVATED":
            impact[name] = "HEADWIND"
        elif snap.status == "DEPRESSED":
            impact[name] = "TAILWIND"
        else:
            impact[name] = "NEUTRAL"
    return impact
