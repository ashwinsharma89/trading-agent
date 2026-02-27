"""
Ratios router.
POST /api/ratio/calculate
GET  /api/ratio/watchlist
POST /api/ratio/watchlist
DELETE /api/ratio/watchlist/{id}
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from config import settings
from models.schemas import (
    AssetSpec,
    RatioCalculateRequest,
    RatioChartData,
    WatchlistCreateRequest,
    WatchlistItem,
)
from services import (
    indian_data_router,
    twelve_data_service,
    fred_service,
    ratio_engine,
)
from cache.redis_cache import get_cache
from database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ratio", tags=["ratios"])

# Timeframe → lookback days
TF_DAYS = {
    "1M": 30, "3M": 90, "6M": 180,
    "1Y": 365, "3Y": 1095, "5Y": 1825,
}


async def _fetch_close(asset: AssetSpec, from_date: str, to_date: str) -> tuple[pd.Series, str]:
    """Fetch closing price series for an asset. Returns (series, note)."""
    note = ""

    if asset.source in ("zerodha", "upstox"):
        df, src_used = await indian_data_router.get_historical_candles(
            asset.key, "day", from_date, to_date
        )
        if df.empty:
            return pd.Series(dtype=float), ""
        series = df.set_index("date")["close"].rename(asset.key)
        if "fallback" in src_used:
            note = f"Using fallback data source ({src_used})"
        return series, note

    elif asset.source == "twelve_data":
        df = await twelve_data_service.get_time_series(
            asset.key,
            interval="1day",
            outputsize=TF_DAYS.get("5Y", 1825),
        )
        if df.empty:
            return pd.Series(dtype=float), ""
        series = df.set_index("date")["close"].rename(asset.key)
        # Trim to requested window
        from_ts = pd.Timestamp(from_date)
        series = series[series.index >= from_ts]
        return series, ""

    elif asset.source == "fred":
        series = await fred_service.get_m2_supply(asset.key, start_date=from_date)
        series.name = asset.key
        note = "M2 interpolated (monthly, forward-filled)"
        return series, note

    raise ValueError(f"Unknown source: {asset.source}")


@router.post("/calculate", response_model=RatioChartData)
async def calculate_ratio(req: RatioCalculateRequest):
    """Calculate and return ratio chart data."""
    days = TF_DAYS.get(req.timeframe, 365)
    today = datetime.today()
    from_date = (today - timedelta(days=days + 60)).strftime("%Y-%m-%d")  # extra buffer
    to_date = today.strftime("%Y-%m-%d")

    cache = get_cache()
    cache_key = f"ratio:{req.asset_a.source}:{req.asset_a.key}:{req.asset_b.source}:{req.asset_b.key}:{req.timeframe}"
    cached = await cache.get(cache_key)
    if cached:
        return RatioChartData(**cached)

    try:
        series_a, note_a = await _fetch_close(req.asset_a, from_date, to_date)
        series_b, note_b = await _fetch_close(req.asset_b, from_date, to_date)
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        raise HTTPException(status_code=502, detail=f"Data fetch failed: {e}")

    if series_a.empty or series_b.empty:
        raise HTTPException(status_code=404, detail="No data returned for one or both assets")

    chart = ratio_engine.get_ratio_chart_data(series_a, series_b)
    note = " | ".join(n for n in [note_a, note_b] if n) or None

    # Trim ratio/zscore/rsi to requested timeframe
    cutoff = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    for key in ("ratio", "zscore", "rsi"):
        chart[key] = [p for p in chart[key] if p["time"] >= cutoff]

    label_a = req.asset_a.label or req.asset_a.key
    label_b = req.asset_b.label or req.asset_b.key

    result = RatioChartData(
        **chart,
        asset_a_label=label_a,
        asset_b_label=label_b,
        note=note,
    )
    await cache.set(cache_key, result.model_dump())
    return result


# ── Watchlist endpoints ───────────────────────────────────────────────────────

@router.get("/watchlist")
async def get_watchlist():
    """Return all saved watchlist items with latest ratio metrics."""
    items = await db.get_watchlist()
    enriched = []
    for item in items:
        try:
            req = RatioCalculateRequest(
                asset_a=item["asset_a"],
                asset_b=item["asset_b"],
                timeframe="1Y",
            )
            data = await calculate_ratio(req)
            enriched.append({
                **item,
                "current_value": data.current_value,
                "current_zscore": data.current_zscore,
                "signal": data.signal,
                "pct_change_1w": data.pct_change_1w,
            })
        except Exception as e:
            logger.warning(f"Could not enrich watchlist item {item.get('id')}: {e}")
            enriched.append(item)
    return {"items": enriched}


@router.post("/watchlist")
async def add_to_watchlist(req: WatchlistCreateRequest):
    item_id = await db.add_watchlist_item(
        name=req.name,
        asset_a=req.asset_a.model_dump(),
        asset_b=req.asset_b.model_dump(),
    )
    return {"id": item_id, "message": "Added to watchlist"}


@router.delete("/watchlist/{item_id}")
async def remove_from_watchlist(item_id: int):
    await db.delete_watchlist_item(item_id)
    return {"message": "Removed from watchlist"}
