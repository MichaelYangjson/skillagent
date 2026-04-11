#!/usr/bin/env python3
"""Ahrefs Site Explorer：site_explorer_organic_keywords（竞品自然关键词，官方 SDK）。"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from ahrefs import AhrefsError
from ahrefs.types import CountryEnum, ModeEnum

from ahrefs_common import get_client, rows_to_jsonable

DEFAULT_SELECT = (
    "keyword,best_position,best_position_url,volume,keyword_difficulty,"
    "sum_traffic,cpc,is_informational,is_commercial,is_transactional,is_navigational"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Ahrefs organic keywords for competitor (SDK: site_explorer_organic_keywords)",
    )
    p.add_argument("--target", required=True, help="Domain or URL")
    p.add_argument(
        "--mode",
        default="subdomains",
        choices=("exact", "prefix", "domain", "subdomains"),
        help="Scope of target",
    )
    p.add_argument("--country", help="ISO country (e.g. us). Omit for API default.")
    p.add_argument(
        "--date",
        help="Report date YYYY-MM-DD. Default: today (UTC).",
    )
    p.add_argument("--select", default=DEFAULT_SELECT, help="Comma-separated columns")
    p.add_argument("--limit", type=int, default=100, help="Row limit")
    p.add_argument("--order-by", dest="order_by", help="order_by column")
    p.add_argument("--out", type=Path, help="JSON output; default stdout")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    report_date = args.date or date.today().isoformat()
    mode = ModeEnum(args.mode)

    country: CountryEnum | None = None
    if args.country:
        try:
            country = CountryEnum(args.country.lower())
        except ValueError as e:
            print(f"Invalid country code: {args.country!r}", file=sys.stderr)
            raise SystemExit(1) from e

    client = get_client()
    try:
        rows = client.site_explorer_organic_keywords(
            select=args.select,
            target=args.target,
            mode=mode,
            date=report_date,
            limit=args.limit,
            country=country,
            order_by=args.order_by,
        )
    except AhrefsError as exc:
        print(f"Ahrefs API error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    payload = {"keywords": rows_to_jsonable(rows)}
    out = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(out, encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
