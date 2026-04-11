#!/usr/bin/env python3
"""Fetch a competitor URL and extract SEO-relevant structure (no JS execution)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from html import unescape
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_UA = (
    "Mozilla/5.0 (compatible; SEO-Opportunity-Mapper/1.0; +https://example.invalid)"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Static HTML competitor page analysis")
    p.add_argument("--url", required=True, help="https://...")
    p.add_argument("--timeout", type=float, default=20.0)
    p.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS certificate verification (debug / broken CA store only)",
    )
    p.add_argument("--out", type=Path, help="JSON path; default stdout")
    return p.parse_args()


def _visible_text_word_count(soup: BeautifulSoup) -> int:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = unescape(text)
    words = re.findall(r"[\w'-]+", text, flags=re.UNICODE)
    return len(words)


def main() -> None:
    args = parse_args()
    headers = {"User-Agent": DEFAULT_UA, "Accept": "text/html,application/xhtml+xml"}
    try:
        r = requests.get(
            args.url,
            headers=headers,
            timeout=args.timeout,
            allow_redirects=True,
            verify=not args.insecure,
        )
    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    ctype = r.headers.get("Content-Type", "")
    if "html" not in ctype.lower() and "text" not in ctype.lower():
        print(f"Unexpected Content-Type: {ctype}", file=sys.stderr)

    soup = BeautifulSoup(r.text, "html.parser")
    base = urlparse(r.url)

    title = soup.title.string.strip() if soup.title and soup.title.string else None
    meta_desc = None
    for m in soup.find_all("meta", attrs={"name": re.compile(r"^description$", re.I)}):
        meta_desc = m.get("content")
        break
    if meta_desc is None:
        for m in soup.find_all("meta", attrs={"property": re.compile(r"og:description", re.I)}):
            meta_desc = m.get("content")
            break

    canonical = None
    for l in soup.find_all("link", attrs={"rel": lambda x: x and "canonical" in x.lower()}):
        canonical = l.get("href")
        break

    def headings(level: int) -> list[str]:
        return [h.get_text(strip=True) for h in soup.find_all(f"h{level}")]

    links = soup.find_all("a", href=True)
    internal = 0
    external = 0
    for a in links:
        href = (a.get("href") or "").strip()
        if href.startswith("#") or href.lower().startswith("javascript:"):
            continue
        if href.startswith("/") or (base.hostname and base.hostname in href):
            internal += 1
        elif href.startswith("http"):
            external += 1

    result = {
        "url_requested": args.url,
        "url_final": r.url,
        "status_code": r.status_code,
        "content_type": ctype,
        "title": title,
        "meta_description": meta_desc,
        "canonical": canonical,
        "h1": headings(1),
        "h2": headings(2),
        "h3": headings(3),
        "heading_dupes": dict(Counter(headings(1) + headings(2) + headings(3))),
        "link_counts": {
            "internal_estimate": internal,
            "external_estimate": external,
            "total_with_href": len(links),
        },
        "word_count_estimate": _visible_text_word_count(BeautifulSoup(r.text, "html.parser")),
        "note": "No JavaScript execution; SPAs may be incomplete.",
    }

    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(out, encoding="utf-8")
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
