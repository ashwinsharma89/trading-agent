# Financial Ratio Chart App

A standalone web application for Indian market traders to monitor and analyse ratio charts (Asset A ÷ Asset B) in real time (15-min delayed data). The app displays the ratio, a rolling z-score, and RSI, and fires signal alerts when ratios reach extreme levels.

---

## Features

- **Ratio charts** with z-score and RSI panels (TradingView `lightweight-charts`)
- **Zerodha Kite Connect** as the primary Indian data source (NSE stocks + indices)
- **Upstox API v2** as an automatic fallback
- **Twelve Data** for global indices and commodities (Gold, WTI, SPX, DAX, …)
- **FRED API** for US M2 money supply (forward-filled to daily)
- **Watchlist** with 8 pre-seeded ratio pairs (Nifty / Gold, BankNifty / Nifty, etc.)
- **Sector Heatmap** — all NSE sector indices vs Nifty 50, colour-coded by z-score
- **Redis caching** with in-memory fallback
- **15-minute background refresh** during market hours (9 AM – 3:45 PM IST, Mon–Fri)
- Dark trading-terminal theme (#0d1117 background, TradingView palette)

---

## Tech Stack

| Layer     | Technology |
|-----------|------------|
| Backend   | Python 3.11, FastAPI, APScheduler |
| Data      | Zerodha Kite Connect, Upstox v2, Twelve Data, FRED |
| Storage   | SQLite (aiosqlite) + Redis |
| Frontend  | Next.js 14, TypeScript, Tailwind CSS |
| Charts    | lightweight-charts v4 (TradingView) |
| State     | Zustand |
| Container | Docker + docker-compose |

---

## Quick Start

### 1. Sign up for API keys

| Service | URL | Cost |
|---------|-----|------|
| Zerodha Kite Connect | https://developers.kite.trade | ₹2 000/month |
| Upstox API (fallback) | https://developer.upstox.com | Free |
| Twelve Data | https://twelvedata.com | Free tier (800 calls/day) |
| FRED | https://fred.stlouisfed.org/docs/api/api_key.html | Free |

### 2. Configure environment

```bash
cd ratio-chart-app/backend
cp .env.example .env
# Fill in all API keys
```

### 3. Zerodha daily auth flow

Zerodha access tokens expire every day at **6 AM IST**. Run this every morning before market open:

```
http://localhost:8000/auth/zerodha/login
```

Complete the Kite login in your browser — the app exchanges the request token for an access token and stores it in Redis automatically.

### 4. Start with Docker

```bash
cd ratio-chart-app
docker-compose up --build
```

Services:
| Service  | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

### 5. Start without Docker (development)

**Backend:**
```bash
cd ratio-chart-app/backend
pip install -r requirements.txt
# Make sure Redis is running locally: redis-server
uvicorn main:app --reload
```

**Frontend:**
```bash
cd ratio-chart-app/frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

---

## Project Structure

```
ratio-chart-app/
├── backend/
│   ├── main.py                     # FastAPI app + auth routes + sector heatmap
│   ├── config.py                   # Pydantic settings (reads .env)
│   ├── database.py                 # SQLite via aiosqlite
│   ├── routers/
│   │   ├── data.py                 # GET /api/instruments/*, /api/price/*
│   │   ├── ratios.py               # POST /api/ratio/calculate, /api/ratio/watchlist
│   │   └── alerts.py              # CRUD /api/alerts
│   ├── services/
│   │   ├── zerodha_service.py      # Kite Connect SDK wrapper
│   │   ├── upstox_service.py       # Upstox v2 REST wrapper
│   │   ├── indian_data_router.py   # Zerodha → Upstox fallback
│   │   ├── twelve_data_service.py  # Twelve Data REST
│   │   ├── fred_service.py         # FRED REST (M2, DGS10, …)
│   │   └── ratio_engine.py         # ratio, z-score, RSI, extremes
│   ├── cache/
│   │   └── redis_cache.py          # Redis + in-memory fallback
│   ├── models/
│   │   └── schemas.py              # Pydantic schemas
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── globals.css
│   │   └── page.tsx                # Dashboard (Watchlist + Chart + Builder)
│   ├── components/
│   │   ├── RatioChart.tsx          # lightweight-charts with sync crosshair
│   │   ├── RatioBuilder.tsx        # Asset picker + timeframe + save
│   │   ├── Watchlist.tsx           # Saved ratios sidebar
│   │   ├── SignalBadge.tsx         # Overbought / Oversold / Neutral badge
│   │   └── SectorHeatmap.tsx       # Sector z-score grid
│   ├── lib/
│   │   ├── api.ts                  # axios API client
│   │   └── store.ts                # Zustand global state
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## API Reference

### Ratio calculation

```
POST /api/ratio/calculate
{
  "asset_a": { "source": "zerodha",     "key": "NSE:NIFTY 50" },
  "asset_b": { "source": "twelve_data", "key": "XAU/USD" },
  "timeframe": "1Y"
}
```

Returns: ratio series, z-score series, RSI series, signal, pct changes.

### Watchlist

```
GET    /api/ratio/watchlist          # list all (with live metrics)
POST   /api/ratio/watchlist          # add { name, asset_a, asset_b }
DELETE /api/ratio/watchlist/{id}     # remove
```

### Instruments

```
GET /api/instruments/search?q=nifty
GET /api/instruments/popular
```

### Auth

```
GET /auth/zerodha/login              # redirect to Kite login
GET /auth/zerodha/callback           # OAuth callback (auto-handled)
GET /auth/zerodha/status             # token validity check
```

---

## Pre-seeded Watchlist Ratios

| Pair | Asset A | Asset B |
|------|---------|---------|
| Nifty / Gold | NSE:NIFTY 50 (Zerodha) | XAU/USD (Twelve Data) |
| Nifty / M2 (US) | NSE:NIFTY 50 | M2SL (FRED) |
| Bank Nifty / Nifty | NSE:NIFTY BANK | NSE:NIFTY 50 |
| Nifty IT / Nifty | NSE:NIFTY IT | NSE:NIFTY 50 |
| Nifty Smallcap / Nifty | NSE:NIFTY SMLCAP 100 | NSE:NIFTY 50 |
| Crude Oil / Gold | WTI | XAU/USD |
| USD/INR / Nifty | USD/INR | NSE:NIFTY 50 |
| Nifty Pharma / Nifty | NSE:NIFTY PHARMA | NSE:NIFTY 50 |

---

## Signal Logic

| Signal | Condition |
|--------|-----------|
| **Overbought** (red badge) | Rolling z-score ≥ +2.0 |
| **Oversold** (green badge) | Rolling z-score ≤ −2.0 |
| **Neutral** (grey badge) | −2.0 < z-score < +2.0 |

Z-score window: 252 days (daily data) or 52 weeks (weekly data).

---

## Important Notes

1. **Zerodha daily re-auth**: Kite Connect tokens expire at 6 AM IST. A banner appears in the UI when re-auth is needed.
2. **Twelve Data free tier**: 800 calls/day. All data is aggressively cached in Redis (15-min TTL for prices, 24 hours for instrument masters).
3. **FRED M2 data**: Monthly observations are forward-filled to daily frequency. Charts note "M2 interpolated (monthly)".
4. **Fallback indicator**: When Upstox is used as fallback, a blue info banner appears in the UI.
5. **MCP server** (optional for Claude Code AI integration):
   ```json
   {
     "mcpServers": {
       "zerodha": {
         "command": "npx",
         "args": ["-y", "kite-connect-mcp"],
         "env": {
           "KITE_API_KEY": "${ZERODHA_API_KEY}",
           "KITE_ACCESS_TOKEN": "${ZERODHA_ACCESS_TOKEN}"
         }
       }
     }
   }
   ```
