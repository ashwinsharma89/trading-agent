"""
Upstox API v2 service — fallback Indian market data source.
"""
import logging
from typing import Any

import httpx
import pandas as pd

from config import settings
from cache.redis_cache import get_cache

logger = logging.getLogger(__name__)

UPSTOX_BASE = "https://api.upstox.com/v2"

# Interval mapping: internal → Upstox API value
INTERVAL_MAP = {
    "day":      "day",
    "week":     "week",
    "month":    "month",
    "60minute": "60minute",
    "30minute": "30minute",
    "15minute": "15minute",
    "1minute":  "1minute",
}

# Known Upstox instrument keys for popular indices
KNOWN_KEYS: dict[str, str] = {
    "NSE:NIFTY 50":         "NSE_INDEX|Nifty 50",
    "NSE:NIFTY BANK":       "NSE_INDEX|Nifty Bank",
    "NSE:NIFTY IT":         "NSE_INDEX|Nifty IT",
    "NSE:NIFTY PHARMA":     "NSE_INDEX|Nifty Pharma",
    "NSE:NIFTY AUTO":       "NSE_INDEX|Nifty Auto",
    "NSE:NIFTY FMCG":       "NSE_INDEX|Nifty FMCG",
    "NSE:NIFTY METAL":      "NSE_INDEX|Nifty Metal",
    "NSE:NIFTY REALTY":     "NSE_INDEX|Nifty Realty",
    "NSE:NIFTY ENERGY":     "NSE_INDEX|Nifty Energy",
    "NSE:NIFTY INFRA":      "NSE_INDEX|Nifty Infrastructure",
    "NSE:NIFTY MEDIA":      "NSE_INDEX|Nifty Media",
    "NSE:NIFTY SMLCAP 100": "NSE_INDEX|Nifty Smallcap 100",
}


def _auth_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.UPSTOX_ACCESS_TOKEN}",
        "Accept": "application/json",
    }


def _to_upstox_key(symbol: str) -> str:
    """Convert a symbol like 'NSE:RELIANCE' to Upstox instrument key."""
    if symbol in KNOWN_KEYS:
        return KNOWN_KEYS[symbol]
    parts = symbol.split(":", 1)
    if len(parts) == 2:
        exchange, ts = parts
        return f"{exchange}_EQ|{ts}"
    return symbol


async def get_historical_candles(
    instrument_key: str,
    interval: str,
    from_date: str,
    to_date: str,
) -> pd.DataFrame:
    """
    Fetch OHLCV from Upstox v2.
    instrument_key: e.g. "NSE_INDEX|Nifty 50" or "NSE_EQ|RELIANCE"
    """
    upstox_key = _to_upstox_key(instrument_key)
    upstox_interval = INTERVAL_MAP.get(interval, "day")
    cache = get_cache()
    cache_key = f"upstox:candles:{upstox_key}:{upstox_interval}:{from_date}:{to_date}"

    cached = await cache.get(cache_key)
    if cached:
        df = pd.DataFrame(cached)
        df["date"] = pd.to_datetime(df["date"])
        return df

    url = f"{UPSTOX_BASE}/historical-candle/{upstox_key}/{upstox_interval}/{to_date}/{from_date}"

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(url, headers=_auth_headers())
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Upstox HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Upstox request failed: {e}")
            raise

    candles = data.get("data", {}).get("candles", [])
    if not candles:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])

    # Upstox format: [timestamp, open, high, low, close, volume, oi]
    rows = []
    for c in candles:
        rows.append({
            "date": pd.Timestamp(c[0]),
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5]),
        })

    df = pd.DataFrame(rows).sort_values("date")
    await cache.set(
        cache_key,
        df.assign(date=df["date"].astype(str)).to_dict("records"),
    )
    return df


async def get_ltp(instrument_keys: list[str]) -> dict[str, Any]:
    upstox_keys = [_to_upstox_key(k) for k in instrument_keys]
    url = f"{UPSTOX_BASE}/market-quote/ltp"
    params = {"instrument_key": ",".join(upstox_keys)}

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url, headers=_auth_headers(), params=params)
            resp.raise_for_status()
            return resp.json().get("data", {})
        except Exception as e:
            logger.error(f"Upstox LTP failed: {e}")
            raise


async def search_instruments(query: str) -> list[dict]:
    """Search Upstox instrument list."""
    url = f"{UPSTOX_BASE}/market-quote/search"
    params = {"query": query, "asset_type": "equity"}

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url, headers=_auth_headers(), params=params)
            resp.raise_for_status()
            items = resp.json().get("data", [])
        except Exception:
            items = []

    results = []
    for item in items[:20]:
        results.append({
            "key": item.get("instrument_key", ""),
            "label": item.get("company_name") or item.get("symbol", ""),
            "source": "upstox",
            "exchange": item.get("exchange"),
            "instrument_type": item.get("instrument_type"),
        })
    return results
