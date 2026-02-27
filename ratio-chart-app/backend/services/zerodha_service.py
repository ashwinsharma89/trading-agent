"""
Zerodha Kite Connect service — primary Indian market data source.

Uses the official kiteconnect Python SDK. Tokens expire at 6 AM IST daily;
the auth flow is handled by routers/auth.py and tokens are stored in Redis.
"""
import logging
from datetime import datetime, date, timedelta
from typing import Any

import pandas as pd

from config import settings
from cache.redis_cache import get_cache

logger = logging.getLogger(__name__)

# Instrument cache key
_INSTRUMENT_CACHE_KEY = "zerodha:instruments:NSE"
_INSTRUMENT_CACHE_TTL = 86400  # 24 hours

# Well-known token map (bootstrap while instrument master downloads)
KNOWN_TOKENS: dict[str, int] = {
    "NSE:NIFTY 50":        256265,
    "NSE:NIFTY BANK":      260105,
    "NSE:NIFTY IT":        259849,
    "NSE:NIFTY PHARMA":    261641,
    "NSE:NIFTY AUTO":      261633,
    "NSE:NIFTY FMCG":      261121,
    "NSE:NIFTY METAL":     261633,
    "NSE:NIFTY REALTY":    261637,
    "NSE:NIFTY ENERGY":    261889,
    "NSE:NIFTY INFRA":     261393,
    "NSE:NIFTY MEDIA":     261641,
    "NSE:NIFTY SMLCAP 100": 270601,
}


def _get_kite():
    """Return an authenticated KiteConnect instance (lazy import)."""
    try:
        from kiteconnect import KiteConnect  # type: ignore
        kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
        kite.set_access_token(settings.ZERODHA_ACCESS_TOKEN)
        return kite
    except ImportError:
        raise RuntimeError(
            "kiteconnect package not installed. "
            "Run: pip install kiteconnect"
        )


async def get_historical_candles(
    instrument_token: int,
    interval: str,
    from_date: str,
    to_date: str,
) -> pd.DataFrame:
    """
    Fetch OHLCV candles from Kite Connect.

    interval options: "day", "week", "month", "60minute", "30minute", "15minute"
    """
    cache = get_cache()
    cache_key = f"zerodha:candles:{instrument_token}:{interval}:{from_date}:{to_date}"

    cached = await cache.get(cache_key)
    if cached:
        df = pd.DataFrame(cached)
        df["date"] = pd.to_datetime(df["date"])
        return df

    kite = _get_kite()

    try:
        data = kite.historical_data(
            instrument_token,
            from_date,
            to_date,
            interval,
        )
        if not data:
            return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])

        await cache.set(cache_key, df.assign(date=df["date"].astype(str)).to_dict("records"))
        return df

    except Exception as e:
        logger.error(f"Zerodha historical_data failed for token {instrument_token}: {e}")
        raise


async def get_ltp(instruments: list[str]) -> dict[str, Any]:
    """
    Get last traded price for a list of instruments.
    instruments: ["NSE:NIFTY 50", "NSE:RELIANCE", ...]
    """
    kite = _get_kite()
    try:
        return kite.ltp(instruments)
    except Exception as e:
        logger.error(f"Zerodha ltp failed: {e}")
        raise


async def get_instrument_token(symbol: str) -> int:
    """
    Resolve a symbol like "NSE:NIFTY 50" to its instrument token integer.
    Checks KNOWN_TOKENS first, then the cached instrument master.
    """
    if symbol in KNOWN_TOKENS:
        return KNOWN_TOKENS[symbol]

    # Strip exchange prefix for master search
    parts = symbol.split(":", 1)
    trading_symbol = parts[1] if len(parts) == 2 else parts[0]

    cache = get_cache()
    instruments = await cache.get(_INSTRUMENT_CACHE_KEY)

    if not instruments:
        instruments = await _download_instrument_master()

    for inst in instruments:
        if inst.get("tradingsymbol") == trading_symbol:
            return inst["instrument_token"]

    raise ValueError(f"Instrument token not found for symbol: {symbol}")


async def _download_instrument_master() -> list[dict]:
    """Download and cache NSE instrument master."""
    kite = _get_kite()
    try:
        logger.info("Downloading Zerodha NSE instrument master…")
        instruments = kite.instruments("NSE")
        # Convert to plain dicts for JSON serialisation
        result = [dict(inst) for inst in instruments]
        cache = get_cache()
        await cache.set(_INSTRUMENT_CACHE_KEY, result, ttl=_INSTRUMENT_CACHE_TTL)
        logger.info(f"Cached {len(result)} NSE instruments")
        return result
    except Exception as e:
        logger.error(f"Failed to download instrument master: {e}")
        return []


async def search_instruments(query: str) -> list[dict]:
    """Search NSE instrument master by trading symbol or name."""
    cache = get_cache()
    instruments = await cache.get(_INSTRUMENT_CACHE_KEY)
    if not instruments:
        instruments = await _download_instrument_master()

    query_lower = query.lower()
    results = []
    for inst in instruments:
        ts = inst.get("tradingsymbol", "").lower()
        name = inst.get("name", "").lower()
        if query_lower in ts or query_lower in name:
            results.append({
                "key": f"NSE:{inst['tradingsymbol']}",
                "label": inst.get("name") or inst["tradingsymbol"],
                "source": "zerodha",
                "exchange": "NSE",
                "instrument_type": inst.get("instrument_type"),
                "instrument_token": inst.get("instrument_token"),
            })
            if len(results) >= 20:
                break
    return results


def is_token_valid() -> bool:
    """Check whether a Zerodha access token is configured."""
    return bool(settings.ZERODHA_ACCESS_TOKEN)
