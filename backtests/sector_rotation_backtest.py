"""Backtest: Sector rotation with commodity overlay."""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import numpy as np
import pandas as pd
import yfinance as yf

SECTOR_TICKERS: Dict[str, str] = {
    "Banking": "^NSEBANK",
    "IT": "^CNXIT",
    "Metals": "^CNXMETAL",
    "Auto": "^CNXAUTO",
    "FMCG": "^CNXFMCG",
    "Energy": "^CNXENERGY",
    "Pharma": "^CNXPHARMA",
}

COMMODITY_LINKS: Dict[str, str] = {
    "Metals": "HG=F",
    "Energy": "BZ=F",
    "Auto": "BZ=F",
    "Banking": None,
    "IT": None,
    "FMCG": "ZC=F",
    "Pharma": None,
}

START_DATE = (datetime.now(timezone.utc) - timedelta(days=365 * 5)).strftime("%Y-%m-%d")
END_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _extract_price_frame(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        if ("Adj Close" in df.columns.get_level_values(0)):
            return df["Adj Close"]
        return df["Close"]
    if "Adj Close" in df.columns:
        return df[["Adj Close"]]
    return df[["Close"]]


def download_prices(symbols: List[str]) -> pd.DataFrame:
    data = yf.download(symbols, start=START_DATE, end=END_DATE, auto_adjust=True, threads=True)
    price_df = _extract_price_frame(data)
    return price_df.dropna()


def compute_monthly_features(prices: pd.DataFrame) -> pd.DataFrame:
    monthly = prices.resample("ME").last().dropna()
    returns = monthly.pct_change().dropna()
    momentum = monthly.pct_change(3).dropna()
    return returns.align(momentum, join="inner")


def commodity_headwind_series(symbol: str, months: pd.Index) -> pd.Series:
    if symbol is None:
        return pd.Series(False, index=months)
    raw = yf.download(symbol, start=START_DATE, end=END_DATE, auto_adjust=True)
    price_series = _extract_price_frame(raw).iloc[:, 0]
    data = price_series.resample("ME").last()
    data = data.reindex(months).ffill()
    rolling = data.rolling(window=12, min_periods=3)
    upper = rolling.quantile(0.75)
    lower = rolling.quantile(0.25)
    return (data >= upper).reindex(months).fillna(False)


def run_backtest() -> Dict[str, float]:
    prices = download_prices(list(SECTOR_TICKERS.values()))
    returns, momentum = compute_monthly_features(prices)
    months = returns.index

    headwinds = {
        sector: commodity_headwind_series(COMMODITY_LINKS.get(sector), months)
        for sector in SECTOR_TICKERS
    }

    portfolio_vals = [1.0]
    baseline_vals = [1.0]

    for i in range(1, len(months)):
        date = months[i]
        section = momentum.loc[date].dropna()
        if section.empty:
            ret = 0
        else:
            ranked = section.sort_values(ascending=False)
            picks = []
            for sector in ranked.index:
                if section[sector] <= 0:
                    continue
                series = headwinds.get(sector)
                if series is not None and bool(series.get(date, False)):
                    continue
                picks.append(sector)
                if len(picks) == 2:
                    break
            if not picks:
                ret = 0
            else:
                ret = returns.loc[date, picks].mean()
        portfolio_vals.append(portfolio_vals[-1] * (1 + ret))
        baseline_vals.append(baseline_vals[-1] * (1 + returns.loc[date].mean()))

    def cagr(values: List[float]) -> float:
        years = len(values) / 12
        return (values[-1] ** (1 / years) - 1) if years > 0 else 0

    def max_drawdown(values: List[float]) -> float:
        cumulative = np.array(values)
        roll_max = np.maximum.accumulate(cumulative)
        drawdowns = (cumulative - roll_max) / roll_max
        return drawdowns.min()

    strat_cagr = cagr(portfolio_vals)
    base_cagr = cagr(baseline_vals)
    strat_dd = max_drawdown(portfolio_vals)
    base_dd = max_drawdown(baseline_vals)

    return {
        "strategy_cagr": strat_cagr,
        "baseline_cagr": base_cagr,
        "strategy_max_dd": strat_dd,
        "baseline_max_dd": base_dd,
        "final_multiple": portfolio_vals[-1],
        "baseline_multiple": baseline_vals[-1],
    }


if __name__ == "__main__":
    stats = run_backtest()
    print("Sector Rotation w/ Commodity Overlay")
    for key, value in stats.items():
        if "cagr" in key:
            print(f"{key}: {value*100:.2f}%")
        else:
            print(f"{key}: {value:.2f}")
