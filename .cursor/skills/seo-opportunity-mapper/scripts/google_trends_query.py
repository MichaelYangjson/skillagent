#!/usr/bin/env python3
"""Google Trends via pytrends: interest over time + related queries."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import pandas as pd
from pytrends.request import TrendReq


def _df_to_records(df: pd.DataFrame | None) -> list[dict] | None:
    if df is None or df.empty:
        return None
    try:
        return df.reset_index().to_dict(orient="records")
    except Exception:
        return None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Google Trends (pytrends)")
    p.add_argument(
        "--keywords",
        required=True,
        help="Comma-separated; max ~5 terms (Google limit)",
    )
    p.add_argument(
        "--geo",
        default="US",
        help="Region, e.g. US, CN, or empty string for worldwide",
    )
    p.add_argument(
        "--timeframe",
        default="today 12-m",
        help='e.g. "today 3-m", "today 12-m", or "2024-01-01 2024-12-31"',
    )
    p.add_argument(
        "--hl",
        default="en-US",
        help="Host language for Google (hl)",
    )
    p.add_argument(
        "--tz",
        type=int,
        default=360,
        help="Timezone offset minutes (pytrends)",
    )
    p.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        help="Seconds to sleep after request (rate limit courtesy)",
    )
    p.add_argument(
        "--out-prefix",
        required=True,
        dest="out_prefix",
        help="Prefix for interest_over_time.csv and related_queries.json",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    kw_list = [k.strip() for k in args.keywords.split(",") if k.strip()]
    if not kw_list:
        print("No keywords after parsing.", file=sys.stderr)
        sys.exit(1)
    if len(kw_list) > 5:
        print("Warning: more than 5 keywords; Trends may error or truncate.", file=sys.stderr)

    geo = args.geo if args.geo is not None else ""
    pytrends = TrendReq(hl=args.hl, tz=args.tz, timeout=(10, 25))
    pytrends.build_payload(kw_list, cat=0, timeframe=args.timeframe, geo=geo, gprop="")

    base = Path(args.out_prefix)
    base.parent.mkdir(parents=True, exist_ok=True)

    iot = pytrends.interest_over_time()
    time.sleep(args.sleep)

    csv_path = Path(str(base) + "_interest_over_time.csv")
    if not iot.empty:
        iot.to_csv(csv_path, encoding="utf-8")
        print(f"Wrote {csv_path}", file=sys.stderr)
    else:
        print("interest_over_time empty (region/timeframe/keywords?)", file=sys.stderr)

    out_rel: dict = {}
    try:
        raw_rel = pytrends.related_queries()
        time.sleep(args.sleep)
        for kw, parts in raw_rel.items():
            if not isinstance(parts, dict):
                out_rel[kw] = str(parts)
                continue
            out_rel[kw] = {
                "top": _df_to_records(parts.get("top")),
                "rising": _df_to_records(parts.get("rising")),
            }
    except Exception as e:
        out_rel = {"_error": str(e)}

    json_path = Path(str(base) + "_related_queries.json")

    json_path.write_text(json.dumps(out_rel, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {json_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
