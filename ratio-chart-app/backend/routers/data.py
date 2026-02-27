"""
Data router — instrument search and price endpoints.
GET /api/instruments/search?q=...
GET /api/instruments/popular
GET /api/price/{instrument_key}
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from services import indian_data_router, twelve_data_service, fred_service
from services import zerodha_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["data"])

# ── Popular instruments hardcoded list ───────────────────────────────────────

POPULAR_INDIAN = [
    {"key": "NSE:NIFTY 50",         "label": "Nifty 50",          "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:NIFTY BANK",       "label": "Nifty Bank",         "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:NIFTY IT",         "label": "Nifty IT",           "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:NIFTY PHARMA",     "label": "Nifty Pharma",       "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:NIFTY AUTO",       "label": "Nifty Auto",         "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:NIFTY FMCG",       "label": "Nifty FMCG",        "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:NIFTY METAL",      "label": "Nifty Metal",        "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:NIFTY REALTY",     "label": "Nifty Realty",       "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:NIFTY ENERGY",     "label": "Nifty Energy",       "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:NIFTY INFRA",      "label": "Nifty Infra",        "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:NIFTY SMLCAP 100", "label": "Nifty Smallcap 100","source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:RELIANCE",         "label": "Reliance Industries", "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:TCS",              "label": "TCS",                 "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:HDFCBANK",         "label": "HDFC Bank",          "source": "zerodha", "exchange": "NSE"},
    {"key": "NSE:INFY",             "label": "Infosys",            "source": "zerodha", "exchange": "NSE"},
]


@router.get("/instruments/search")
async def search_instruments(q: str = Query(..., min_length=1)):
    """Search across Indian stocks/indices and global instruments."""
    results = []

    # Indian instruments
    try:
        indian = await indian_data_router.search_instruments(q)
        results.extend(indian)
    except Exception as e:
        logger.warning(f"Indian instrument search failed: {e}")

    # Twelve Data symbols (simple prefix match on popular list)
    q_lower = q.lower()
    for item in twelve_data_service.list_popular():
        if q_lower in item["key"].lower() or q_lower in item["label"].lower():
            results.append(item)

    # FRED series
    for item in fred_service.FRED_POPULAR:
        if q_lower in item["key"].lower() or q_lower in item["label"].lower():
            results.append(item)

    return {"results": results[:30]}


@router.get("/instruments/popular")
async def popular_instruments():
    return {
        "indian": POPULAR_INDIAN,
        "global": twelve_data_service.list_popular(),
        "fred":   fred_service.FRED_POPULAR,
    }


@router.get("/price/{instrument_key:path}")
async def get_price(
    instrument_key: str,
    source: Optional[str] = Query(None),
    timeframe: str = Query("1Y"),
):
    """
    Return OHLCV data for a single instrument.
    instrument_key: URL-encoded instrument key
    source: zerodha | upstox | twelve_data | fred
    """
    from datetime import date

    today = date.today().isoformat()
    timeframe_days = {
        "1M": 30, "3M": 90, "6M": 180,
        "1Y": 365, "3Y": 1095, "5Y": 1825,
    }
    days = timeframe_days.get(timeframe, 365)
    from_date = (datetime.today() - timedelta(days=days)).strftime("%Y-%m-%d")

    detected_source = source
    if not detected_source:
        if instrument_key.startswith("NSE:") or instrument_key.startswith("BSE:"):
            detected_source = "zerodha"
        elif "/" in instrument_key or instrument_key in [
            "WTI", "SPX", "DJI", "DAX", "NI225", "HSI"
        ]:
            detected_source = "twelve_data"
        elif instrument_key.isupper() and len(instrument_key) <= 8:
            detected_source = "fred"
        else:
            detected_source = "zerodha"

    try:
        if detected_source in ("zerodha", "upstox"):
            df, _ = await indian_data_router.get_historical_candles(
                instrument_key, "day", from_date, today
            )
        elif detected_source == "twelve_data":
            df = await twelve_data_service.get_time_series(
                instrument_key, "1day", days
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported source: {detected_source}")

        if df.empty:
            return {"candles": []}

        candles = []
        for _, row in df.iterrows():
            dt = row["date"]
            candles.append({
                "time":   dt.strftime("%Y-%m-%d") if hasattr(dt, "strftime") else str(dt)[:10],
                "open":   float(row.get("open", 0)),
                "high":   float(row.get("high", 0)),
                "low":    float(row.get("low", 0)),
                "close":  float(row["close"]),
                "volume": float(row.get("volume", 0)),
            })
        return {"candles": candles, "source": detected_source}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Price fetch failed for {instrument_key}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
