"""Automated alert manager for macro, sector, and commodity events."""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, List

import requests

from market_data_fetcher import MarketDataFetcher
from commodity_data_fetcher import fetch_commodity_snapshot

SECTOR_ALERT_THRESHOLDS = {
    "BreadthUpper": 0.75,
    "BreadthLower": 0.25,
    "ChangeUpper": 1.5,
    "ChangeLower": -1.5,
}

COMMODITY_ALERTS = {
    "Brent Crude": {"upper": 95, "lower": 75},
    "Henry Hub Gas": {"upper": 4.5, "lower": 2.5},
    "LME Copper": {"upper": 9500, "lower": 7800},
    "Gold": {"upper": 2250, "lower": 1900},
}

SLACK_WEBHOOK = os.getenv("ALERT_WEBHOOK_URL") or os.getenv("SLACK_WEBHOOK_URL")

def build_sector_alerts(fetcher: MarketDataFetcher) -> List[str]:
    alerts: List[str] = []
    sector_data = fetcher.get_sector_data(getattr(fetcher, "sector_watchlist", {}))
    for sector, metrics in sector_data.items():
        score = metrics.get("score", 0.5)
        change = metrics.get("change", 0.0)
        if score >= SECTOR_ALERT_THRESHOLDS["BreadthUpper"]:
            alerts.append(f"🔥 Sector breadth hot: {sector} score {score:.2f}")
        if score <= SECTOR_ALERT_THRESHOLDS["BreadthLower"]:
            alerts.append(f"🥶 Sector breadth weak: {sector} score {score:.2f}")
        if change >= SECTOR_ALERT_THRESHOLDS["ChangeUpper"]:
            alerts.append(f"📈 {sector} avg change {change:+.2f}%")
        if change <= SECTOR_ALERT_THRESHOLDS["ChangeLower"]:
            alerts.append(f"📉 {sector} avg change {change:+.2f}%")
    return alerts


def build_commodity_alerts() -> List[str]:
    alerts: List[str] = []
    snapshots = fetch_commodity_snapshot()
    for name, snap in snapshots.items():
        bands = COMMODITY_ALERTS.get(name)
        if not bands:
            continue
        if snap.price >= bands["upper"]:
            alerts.append(f"⚠️ {name} elevated at {snap.price:.2f}")
        if snap.price <= bands["lower"]:
            alerts.append(f"✅ {name} benign at {snap.price:.2f}")
    return alerts


def dispatch_alerts(messages: List[str]) -> None:
    if not messages:
        return
    payload = {
        "text": "\n".join(["🚨 Enterprise Alerts – " + datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), ""] + messages)
    }
    if SLACK_WEBHOOK:
        try:
            response = requests.post(SLACK_WEBHOOK, json=payload, timeout=10)
            response.raise_for_status()
        except Exception as exc:  # pragma: no cover - network call
            print(f"Failed to post alert: {exc}")
    else:
        print(json.dumps(payload, indent=2))


def run_alert_cycle() -> None:
    fetcher = MarketDataFetcher()
    sector_msgs = build_sector_alerts(fetcher)
    commodity_msgs = build_commodity_alerts()
    dispatch_alerts(sector_msgs + commodity_msgs)


if __name__ == "__main__":
    run_alert_cycle()
