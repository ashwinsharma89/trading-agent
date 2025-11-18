"""Streamlit dashboard for macro, sector, and commodity monitoring."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Dict

import pandas as pd
import streamlit as st
import yfinance as yf

from market_data_fetcher import MarketDataFetcher
from commodity_data_fetcher import fetch_commodity_snapshot

st.set_page_config(page_title="Macro & Sector Dashboard", page_icon="🌐", layout="wide")

st.title("🌐 Macro + Sector Intelligence Console")
st.caption("Live view of index momentum, sector breadth, and commodity pressures")

fetcher = MarketDataFetcher()
SECTOR_DATA = fetcher.get_sector_data(getattr(fetcher, "sector_watchlist", {})) or {}

@st.cache_data(ttl=900)
def fetch_index(symbol: str) -> Dict[str, float]:
    data = yf.Ticker(symbol).history(period="3mo", interval="1d")
    if data.empty:
        return {"symbol": symbol, "price": float("nan"), "change": 0.0, "change_pct": 0.0}
    latest = data.iloc[-1]
    prev = data.iloc[-2] if len(data) > 1 else latest
    change = latest["Close"] - prev["Close"]
    change_pct = (change / prev["Close"]) * 100 if prev["Close"] else 0
    return {
        "symbol": symbol,
        "price": float(latest["Close"]),
        "change": float(change),
        "change_pct": float(change_pct),
    }

macro_cols = st.columns(3)
indices = {"Nifty 50": "^NSEI", "S&P 500": "^GSPC", "US 10Y": "^TNX"}
for col, (name, symbol) in zip(macro_cols, indices.items()):
    idx = fetch_index(symbol)
    col.metric(name, f"{idx['price']:.2f}", f"{idx['change_pct']:+.2f}%")

st.markdown("---")
left, right = st.columns([1.5, 1])

with left:
    st.subheader("Sector Momentum Snapshot")
    if SECTOR_DATA:
        sector_df = (
            pd.DataFrame.from_dict(SECTOR_DATA, orient="index")
            .reset_index()
            .rename(columns={"index": "Sector", "change": "Avg % Change", "score": "Breadth Score"})
        )
        st.dataframe(
            sector_df.sort_values("Breadth Score", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Sector data unavailable; ensure MarketDataFetcher watchlist is populated.")

with right:
    st.subheader("Commodity Monitor")
    snapshots = fetch_commodity_snapshot()
    commodity_df = pd.DataFrame([
        {
            "Commodity": name,
            "Price": f"{snap.price:.2f}",
            "Daily %": f"{snap.change_pct:+.2f}%",
            "Trend": snap.trend,
            "Status": snap.status,
        }
        for name, snap in snapshots.items()
    ])
    st.dataframe(commodity_df, hide_index=True, use_container_width=True)

st.markdown("---")
st.caption(f"Last Refresh: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
