"""
Indian data router — tries Zerodha first, falls back to Upstox.
"""
import logging
from typing import Any

import pandas as pd

from config import settings
from services import zerodha_service, upstox_service

logger = logging.getLogger(__name__)


async def get_historical_candles(
    symbol: str,
    interval: str,
    from_date: str,
    to_date: str,
) -> tuple[pd.DataFrame, str]:
    """
    Returns (DataFrame, source_used).
    symbol: e.g. "NSE:NIFTY 50" or "NSE:RELIANCE"
    """
    source = settings.INDIAN_DATA_SOURCE

    async def _zerodha() -> pd.DataFrame:
        token = await zerodha_service.get_instrument_token(symbol)
        return await zerodha_service.get_historical_candles(token, interval, from_date, to_date)

    async def _upstox() -> pd.DataFrame:
        return await upstox_service.get_historical_candles(symbol, interval, from_date, to_date)

    if source == "zerodha":
        try:
            df = await _zerodha()
            return df, "zerodha"
        except Exception as e:
            logger.warning(f"Zerodha failed ({e}); falling back to Upstox")
            try:
                df = await _upstox()
                return df, "upstox (fallback)"
            except Exception as e2:
                logger.error(f"Upstox fallback also failed: {e2}")
                raise
    else:
        try:
            df = await _upstox()
            return df, "upstox"
        except Exception as e:
            logger.warning(f"Upstox failed ({e}); falling back to Zerodha")
            df = await _zerodha()
            return df, "zerodha (fallback)"


async def get_ltp(instruments: list[str]) -> tuple[dict[str, Any], str]:
    source = settings.INDIAN_DATA_SOURCE
    if source == "zerodha":
        try:
            data = await zerodha_service.get_ltp(instruments)
            return data, "zerodha"
        except Exception as e:
            logger.warning(f"Zerodha LTP failed ({e}); falling back to Upstox")
            data = await upstox_service.get_ltp(instruments)
            return data, "upstox (fallback)"
    else:
        try:
            data = await upstox_service.get_ltp(instruments)
            return data, "upstox"
        except Exception as e:
            logger.warning(f"Upstox LTP failed ({e}); falling back to Zerodha")
            data = await zerodha_service.get_ltp(instruments)
            return data, "zerodha (fallback)"


async def search_instruments(query: str) -> list[dict]:
    source = settings.INDIAN_DATA_SOURCE
    try:
        if source == "zerodha":
            return await zerodha_service.search_instruments(query)
        else:
            return await upstox_service.search_instruments(query)
    except Exception as e:
        logger.warning(f"Instrument search failed ({e}); trying other source")
        if source == "zerodha":
            return await upstox_service.search_instruments(query)
        return await zerodha_service.search_instruments(query)
