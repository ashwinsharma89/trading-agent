"""Command-line utility to log hedge tickets and prepare downstream execution."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

LOG_DIR = Path("logs/hedges")
LOG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class HedgeTicket:
    strategy: str
    timestamp: str
    params: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hedge execution ticket generator")
    parser.add_argument("--strategy", required=True, help="Strategy name: fuel/agri/fx/metals/carbon")
    parser.add_argument("--commodity", help="Commodity code (wheat, sugar, copper)")
    parser.add_argument("--pair", help="FX pair, e.g. USDINR")
    parser.add_argument("--instrument", help="Instrument type (forward, swap, call_spread)")
    parser.add_argument("--notional", type=float, help="Notional amount (bbl, USD, tonnes)")
    parser.add_argument("--lots", type=int, help="Number of futures lots")
    parser.add_argument("--tenor", help="Tenor (e.g. 3M, 2025-06)")
    parser.add_argument("--expiry", help="Option expiry date (YYYY-MM-DD)")
    parser.add_argument("--type", dest="trade_type", help="Forward/option type")
    parser.add_argument("--notes", help="Free-text notes")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    params = {k: v for k, v in vars(args).items() if v is not None and k != "strategy"}
    ticket = HedgeTicket(strategy=args.strategy, timestamp=timestamp, params=params)
    file_path = LOG_DIR / f"{timestamp}_{args.strategy}.json"
    file_path.write_text(ticket.to_json())
    print(f"✅ Hedge ticket saved to {file_path}")


if __name__ == "__main__":
    main()
