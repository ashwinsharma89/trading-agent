"""
SQLite database layer using aiosqlite.
Tables: watchlist, alerts
"""
import json
import logging
from datetime import datetime
from typing import Any

import aiosqlite

from config import settings

logger = logging.getLogger(__name__)

DB_PATH = settings.DB_PATH


async def init_db():
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.executescript("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                asset_a    TEXT    NOT NULL,   -- JSON
                asset_b    TEXT    NOT NULL,   -- JSON
                created_at TEXT    DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                name         TEXT    NOT NULL,
                asset_a      TEXT    NOT NULL,
                asset_b      TEXT    NOT NULL,
                condition    TEXT    NOT NULL,
                threshold    REAL    NOT NULL,
                notify_via   TEXT    DEFAULT 'ui',
                is_active    INTEGER DEFAULT 1,
                triggered_at TEXT,
                created_at   TEXT    DEFAULT (datetime('now'))
            );
        """)
        await conn.commit()
    logger.info("Database initialised")

    # Seed default watchlist if empty
    await _seed_defaults()


DEFAULT_WATCHLIST = [
    {"name": "Nifty / Gold",            "a_key": "NSE:NIFTY 50",         "a_src": "zerodha",     "b_key": "XAU/USD",         "b_src": "twelve_data"},
    {"name": "Nifty / M2 (US)",         "a_key": "NSE:NIFTY 50",         "a_src": "zerodha",     "b_key": "M2SL",            "b_src": "fred"},
    {"name": "Bank Nifty / Nifty",      "a_key": "NSE:NIFTY BANK",       "a_src": "zerodha",     "b_key": "NSE:NIFTY 50",    "b_src": "zerodha"},
    {"name": "Nifty IT / Nifty",        "a_key": "NSE:NIFTY IT",         "a_src": "zerodha",     "b_key": "NSE:NIFTY 50",    "b_src": "zerodha"},
    {"name": "Nifty Smallcap / Nifty",  "a_key": "NSE:NIFTY SMLCAP 100","a_src": "zerodha",     "b_key": "NSE:NIFTY 50",    "b_src": "zerodha"},
    {"name": "Crude Oil / Gold",         "a_key": "WTI",                  "a_src": "twelve_data", "b_key": "XAU/USD",         "b_src": "twelve_data"},
    {"name": "USD/INR / Nifty",         "a_key": "USD/INR",              "a_src": "twelve_data", "b_key": "NSE:NIFTY 50",    "b_src": "zerodha"},
    {"name": "Nifty Pharma / Nifty",    "a_key": "NSE:NIFTY PHARMA",    "a_src": "zerodha",     "b_key": "NSE:NIFTY 50",    "b_src": "zerodha"},
]


async def _seed_defaults():
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("SELECT COUNT(*) FROM watchlist")
        (count,) = await cursor.fetchone()
        if count > 0:
            return
        for item in DEFAULT_WATCHLIST:
            asset_a = json.dumps({"source": item["a_src"], "key": item["a_key"], "label": item["a_key"]})
            asset_b = json.dumps({"source": item["b_src"], "key": item["b_key"], "label": item["b_key"]})
            await conn.execute(
                "INSERT INTO watchlist (name, asset_a, asset_b) VALUES (?, ?, ?)",
                (item["name"], asset_a, asset_b),
            )
        await conn.commit()
    logger.info("Seeded default watchlist")


# ── Watchlist CRUD ────────────────────────────────────────────────────────────

async def get_watchlist() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT id, name, asset_a, asset_b, created_at FROM watchlist ORDER BY id"
        )
        rows = await cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            "id":   row["id"],
            "name": row["name"],
            "asset_a": json.loads(row["asset_a"]),
            "asset_b": json.loads(row["asset_b"]),
            "created_at": row["created_at"],
        })
    return result


async def add_watchlist_item(name: str, asset_a: dict, asset_b: dict) -> int:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "INSERT INTO watchlist (name, asset_a, asset_b) VALUES (?, ?, ?)",
            (name, json.dumps(asset_a), json.dumps(asset_b)),
        )
        await conn.commit()
        return cursor.lastrowid


async def delete_watchlist_item(item_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM watchlist WHERE id = ?", (item_id,))
        await conn.commit()


# ── Alerts CRUD ───────────────────────────────────────────────────────────────

async def create_alert(
    name: str,
    asset_a: dict,
    asset_b: dict,
    condition: str,
    threshold: float,
    notify_via: str = "ui",
) -> int:
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            """INSERT INTO alerts (name, asset_a, asset_b, condition, threshold, notify_via)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, json.dumps(asset_a), json.dumps(asset_b), condition, threshold, notify_via),
        )
        await conn.commit()
        return cursor.lastrowid


async def get_alerts() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            "SELECT * FROM alerts WHERE is_active = 1 ORDER BY id"
        )
        rows = await cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            "id":           row["id"],
            "name":         row["name"],
            "asset_a":      json.loads(row["asset_a"]),
            "asset_b":      json.loads(row["asset_b"]),
            "condition":    row["condition"],
            "threshold":    row["threshold"],
            "notify_via":   row["notify_via"],
            "is_active":    bool(row["is_active"]),
            "triggered_at": row["triggered_at"],
            "created_at":   row["created_at"],
        })
    return result


async def delete_alert(alert_id: int):
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
        await conn.commit()
