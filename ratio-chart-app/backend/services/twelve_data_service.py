"""
Twelve Data API service — global indices and commodities.
Free tier: 800 API calls/day → cache aggressively.
"""
import logging
from datetime import datetime, timedelta

import httpx
import pandas as pd

from config import settings
from cache.redis_cache import get_cache

logger = logging.getLogger(__name__)

TWELVE_BASE = "https://api.twelvedata.com"

# Twelve Data supports these outputsizes per request (max 5000 on paid, 5000 on free with 800/day)
TIMEFRAME_TO_INTERVAL = {
    "1M":  ("1day",  30),
    "3M":  ("1day",  90),
    "6M":  ("1day",  180),
    "1Y":  ("1day",  365),
    "3Y":  ("1week", 156),   # 3 years of weeks
    "5Y":  ("1week", 260),   # 5 years of weeks
}

# Well-known symbols
POPULAR_SYMBOLS = {
    "Gold":      "XAU/USD",
    "Silver":    "XAG/USD",
    "Crude WTI": "WTI",
    "S&P 500":   "SPX",
    "Dow Jones": "DJI",
    "DAX":       "DAX",
    "Nikkei":    "NI225",
    "Hang Seng": "HSI",
    "USD/INR":   "USD/INR",
    "EUR/USD":   "EUR/USD",
    "BTC/USD":   "BTC/USD",
}


async def get_time_series(
    symbol: str,
    interval: str = "1day",
    outputsize: int = 365,
) -> pd.DataFrame:
    """
    Fetch time series from Twelve Data.
    Returns DataFrame with columns: date, open, high, low, close, volume
    """
    cache = get_cache()
    cache_key = f"twelve:{symbol}:{interval}:{outputsize}"

    cached = await cache.get(cache_key)
    if cached:
        df = pd.DataFrame(cached)
        df["date"] = pd.to_datetime(df["date"])
        return df

    if not settings.TWELVE_DATA_API_KEY:
        raise RuntimeError("TWELVE_DATA_API_KEY is not set")

    url = f"{TWELVE_BASE}/time_series"
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": outputsize,
        "apikey": settings.TWELVE_DATA_API_KEY,
        "order": "ASC",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Twelve Data HTTP {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Twelve Data request failed: {e}")
            raise

    if data.get("status") == "error":
        raise RuntimeError(f"Twelve Data error: {data.get('message')}")

    values = data.get("values", [])
    if not values:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])

    rows = []
    for v in values:
        rows.append({
            "date": pd.Timestamp(v["datetime"]),
            "open": float(v.get("open", 0) or 0),
            "high": float(v.get("high", 0) or 0),
            "low":  float(v.get("low", 0) or 0),
            "close": float(v["close"]),
            "volume": float(v.get("volume", 0) or 0),
        })

    df = pd.DataFrame(rows).sort_values("date")
    await cache.set(
        cache_key,
        df.assign(date=df["date"].astype(str)).to_dict("records"),
    )
    return df


async def get_close_series(
    symbol: str,
    timeframe: str = "1Y",
) -> pd.Series:
    """Return close price Series indexed by date for a given timeframe."""
    interval, outputsize = TIMEFRAME_TO_INTERVAL.get(timeframe, ("1day", 365))
    df = await get_time_series(symbol, interval, outputsize)
    if df.empty:
        return pd.Series(dtype=float)
    return df.set_index("date")["close"].rename(symbol)


def list_popular() -> list[dict]:
    return [
        {"key": v, "label": k, "source": "twelve_data"}
        for k, v in POPULAR_SYMBOLS.items()
    ]
