#!/usr/bin/env python3
"""Ahrefs Keywords Explorer：keywords_explorer_overview（官方 SDK）。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from ahrefs import AhrefsError
from ahrefs.types import CountryEnum

from ahrefs_common import get_client, rows_to_jsonable

DEFAULT_SELECT = (
    "keyword,volume,difficulty,clicks,cpc,traffic_potential,intents,"
    "serp_features,parent_topic,parent_volume,global_volume"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Ahrefs keyword overview (SDK: keywords_explorer_overview)",
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--keywords", help="Comma-separated keywords")
    g.add_argument("--keywords-file", type=Path, help="One keyword per line")
    p.add_argument(
        "--country",
        required=True,
        help="ISO 3166-1 alpha-2 country code (e.g. us, gb)",
    )
    p.add_argument(
        "--select",
        default=DEFAULT_SELECT,
        help="Comma-separated columns (Ahrefs API field names)",
    )
    p.add_argument("--limit", type=int, default=100, help="Max rows")
    p.add_argument("--out", type=Path, help="Write JSON; default stdout")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.keywords_file:
        text = args.keywords_file.read_text(encoding="utf-8")
        kws = [ln.strip() for ln in text.splitlines() if ln.strip()]
        keywords = ",".join(kws)
    else:
        parts = [p.strip() for p in args.keywords.split(",") if p.strip()]
        keywords = ",".join(parts)

    try:
        country = CountryEnum(args.country.lower())
    except ValueError as e:
        print(f"Invalid country code: {args.country!r}", file=sys.stderr)
        raise SystemExit(1) from e

    client = get_client()
    try:
        rows = client.keywords_explorer_overview(
            select=args.select,
            country=country,
            keywords=keywords,
            limit=args.limit,
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
