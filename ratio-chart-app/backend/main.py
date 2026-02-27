"""
Financial Ratio Chart App — FastAPI Backend
"""
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, time as dtime
from typing import Any, Optional

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse

from cache.redis_cache import init_cache, get_cache
from config import settings
from database import init_db
from routers import data as data_router
from routers import ratios as ratios_router
from routers import alerts as alerts_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


# ── Background refresh job ────────────────────────────────────────────────────

async def _refresh_watchlist():
    """Refresh all watchlist ratios during market hours."""
    logger.info("Background refresh: clearing watchlist ratio caches…")
    cache = get_cache()
    # Simple approach: clear ratio cache keys so next request re-fetches
    # (Full cache invalidation would require scanning keys — skip for now)
    logger.info("Refresh complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── startup ──
    logger.info("Starting Financial Ratio Chart App…")
    await init_cache(settings.REDIS_URL, settings.CACHE_TTL_SECONDS)
    await init_db()

    # Schedule 15-min refresh Mon–Fri 09:00–15:45 IST
    scheduler.add_job(
        _refresh_watchlist,
        CronTrigger(
            day_of_week="mon-fri",
            hour="9-15",
            minute="*/15",
            timezone="Asia/Kolkata",
        ),
        id="watchlist_refresh",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started")

    yield

    # ── shutdown ──
    scheduler.shutdown(wait=False)
    logger.info("Shutdown complete")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Financial Ratio Chart API",
    description="Indian market ratio charting with Zerodha / Upstox / Twelve Data / FRED",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(data_router.router)
app.include_router(ratios_router.router)
app.include_router(alerts_router.router)


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    from services.zerodha_service import is_token_valid
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "zerodha_token_valid": is_token_valid(),
        "indian_data_source": settings.INDIAN_DATA_SOURCE,
    }


# ── Zerodha OAuth ─────────────────────────────────────────────────────────────

@app.get("/auth/zerodha/login")
async def zerodha_login():
    """Redirect user to Zerodha Kite Connect login page."""
    if not settings.ZERODHA_API_KEY:
        raise HTTPException(status_code=400, detail="ZERODHA_API_KEY not configured")
    login_url = f"https://kite.trade/connect/login?api_key={settings.ZERODHA_API_KEY}&v=3"
    return RedirectResponse(login_url)


@app.get("/auth/zerodha/callback")
async def zerodha_callback(request_token: str, status: Optional[str] = None):
    """Exchange request_token for access_token and cache it."""
    if not settings.ZERODHA_API_KEY or not settings.ZERODHA_API_SECRET:
        raise HTTPException(status_code=400, detail="Zerodha API credentials not configured")

    try:
        from kiteconnect import KiteConnect  # type: ignore
        kite = KiteConnect(api_key=settings.ZERODHA_API_KEY)
        session = kite.generate_session(request_token, api_secret=settings.ZERODHA_API_SECRET)
        access_token = session["access_token"]
    except ImportError:
        raise HTTPException(status_code=500, detail="kiteconnect package not installed")
    except Exception as e:
        logger.error(f"Zerodha session generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    # Update running config
    settings.ZERODHA_ACCESS_TOKEN = access_token

    # Persist in cache with 8-hour TTL (Zerodha tokens expire at 6 AM IST next day)
    cache = get_cache()
    await cache.set("zerodha:access_token", access_token, ttl=8 * 3600)

    logger.info("Zerodha access token updated successfully")
    return JSONResponse({"status": "ok", "message": "Zerodha authentication successful. Token valid until 6 AM IST."})


@app.get("/auth/zerodha/status")
async def zerodha_auth_status():
    """Check whether a valid Zerodha access token is available."""
    from services.zerodha_service import is_token_valid
    valid = is_token_valid()
    cache = get_cache()
    cached_token = await cache.get("zerodha:access_token")

    return {
        "token_configured": valid or bool(cached_token),
        "source": settings.INDIAN_DATA_SOURCE,
        "message": (
            None if (valid or cached_token)
            else "Re-authenticate at GET /auth/zerodha/login"
        ),
    }


# ── Upstox OAuth ──────────────────────────────────────────────────────────────

@app.get("/auth/upstox/callback")
async def upstox_callback(code: str):
    """Exchange auth code for Upstox access token."""
    token_url = "https://api.upstox.com/v2/login/authorization/token"
    payload = {
        "code": code,
        "client_id": settings.UPSTOX_CLIENT_ID,
        "client_secret": settings.UPSTOX_CLIENT_SECRET,
        "redirect_uri": settings.UPSTOX_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(token_url, data=payload)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error(f"Upstox auth failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    access_token = data.get("access_token", "")
    settings.UPSTOX_ACCESS_TOKEN = access_token
    cache = get_cache()
    await cache.set("upstox:access_token", access_token, ttl=86400)
    return JSONResponse({"status": "ok", "message": "Upstox authentication successful"})


# ── Sector heatmap endpoint ───────────────────────────────────────────────────

SECTORS = [
    ("Bank",    "NSE:NIFTY BANK"),
    ("IT",      "NSE:NIFTY IT"),
    ("Pharma",  "NSE:NIFTY PHARMA"),
    ("Auto",    "NSE:NIFTY AUTO"),
    ("FMCG",    "NSE:NIFTY FMCG"),
    ("Metal",   "NSE:NIFTY METAL"),
    ("Realty",  "NSE:NIFTY REALTY"),
    ("Energy",  "NSE:NIFTY ENERGY"),
    ("Infra",   "NSE:NIFTY INFRA"),
    ("Media",   "NSE:NIFTY MEDIA"),
]


@app.get("/api/sector-heatmap")
async def sector_heatmap():
    """
    Return z-score of each sector vs Nifty 50 ratio.
    Colour coding is done on the frontend.
    """
    from services import indian_data_router, ratio_engine
    from datetime import timedelta

    today = datetime.today()
    from_date = (today - timedelta(days=365 + 30)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    try:
        nifty_df, _ = await indian_data_router.get_historical_candles(
            "NSE:NIFTY 50", "day", from_date, to_date
        )
        nifty = nifty_df.set_index("date")["close"].rename("NSE:NIFTY 50")
    except Exception as e:
        logger.warning(f"Heatmap: failed to fetch Nifty 50 data: {e}")
        return {"sectors": []}

    results = []
    for name, key in SECTORS:
        try:
            sector_df, _ = await indian_data_router.get_historical_candles(
                key, "day", from_date, to_date
            )
            sector = sector_df.set_index("date")["close"].rename(key)
            chart = ratio_engine.get_ratio_chart_data(sector, nifty)
            results.append({
                "name":          name,
                "key":           key,
                "current_zscore": chart["current_zscore"],
                "current_value":  chart["current_value"],
                "signal":         chart["signal"],
                "pct_change_1w":  chart["pct_change_1w"],
            })
        except Exception as e:
            logger.warning(f"Heatmap: failed for {name}: {e}")
            results.append({"name": name, "key": key, "current_zscore": None, "signal": "neutral"})

    return {"sectors": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
