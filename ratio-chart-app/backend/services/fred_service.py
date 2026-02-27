"""
FRED API service — US M2 money supply (and optional India M2).
Monthly data, forward-filled to daily.
"""
import logging
from datetime import datetime

import httpx
import pandas as pd

from config import settings
from cache.redis_cache import get_cache

logger = logging.getLogger(__name__)

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"
FRED_CACHE_TTL = 86400 * 7  # refresh weekly (FRED updates monthly)


async def get_series(
    series_id: str = "M2SL",
    start_date: str = "2010-01-01",
) -> pd.Series:
    """
    Fetch a FRED data series and return a daily-frequency Series
    (forward-filled from the original monthly/weekly observations).
    """
    cache = get_cache()
    cache_key = f"fred:{series_id}:{start_date}"

    cached = await cache.get(cache_key)
    if cached:
        s = pd.Series(cached["values"], index=pd.to_datetime(cached["index"]))
        return s.rename(series_id)

    if not settings.FRED_API_KEY:
        raise RuntimeError("FRED_API_KEY is not set")

    params = {
        "series_id": series_id,
        "observation_start": start_date,
        "api_key": settings.FRED_API_KEY,
        "file_type": "json",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(FRED_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error(f"FRED request failed for {series_id}: {e}")
            raise

    observations = data.get("observations", [])
    if not observations:
        return pd.Series(dtype=float, name=series_id)

    raw_dates, raw_values = [], []
    for obs in observations:
        val = obs.get("value", ".")
        if val == ".":
            continue
        raw_dates.append(pd.Timestamp(obs["date"]))
        raw_values.append(float(val))

    if not raw_dates:
        return pd.Series(dtype=float, name=series_id)

    s = pd.Series(raw_values, index=raw_dates, name=series_id)
    s = s.sort_index()

    # Forward-fill to daily frequency up to today
    daily_idx = pd.date_range(s.index[0], datetime.today(), freq="D")
    s = s.reindex(daily_idx).ffill()

    # Store in cache
    await cache.set(
        cache_key,
        {
            "index": s.index.astype(str).tolist(),
            "values": s.tolist(),
        },
        ttl=FRED_CACHE_TTL,
    )

    return s.rename(series_id)


async def get_m2_supply(
    series_id: str = "M2SL",
    start_date: str = "2010-01-01",
) -> pd.Series:
    return await get_series(series_id, start_date)


FRED_POPULAR = [
    {"key": "M2SL",  "label": "US M2 Money Supply", "source": "fred"},
    {"key": "M1SL",  "label": "US M1 Money Supply", "source": "fred"},
    {"key": "BASE",  "label": "US Monetary Base",    "source": "fred"},
    {"key": "FEDFUNDS", "label": "Fed Funds Rate",   "source": "fred"},
    {"key": "DGS10", "label": "US 10Y Treasury Yield", "source": "fred"},
    {"key": "DGS2",  "label": "US 2Y Treasury Yield",  "source": "fred"},
]
