#!/usr/bin/env python3
"""
Call the Open Legal Codes REST API (no API key required).

Docs: https://openlegalcodes.org/developers
Base URL: https://openlegalcodes.org/api/v1
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://openlegalcodes.org/api/v1"


def request_json(path: str, query: dict[str, str] | None = None) -> tuple[int, object]:
    """GET path (leading slash optional). Returns (http_status, parsed JSON)."""
    q = f"?{urllib.parse.urlencode(query)}" if query else ""
    url = f"{BASE}{path if path.startswith('/') else '/' + path}{q}"
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        status = resp.getcode()
        raw = resp.read().decode("utf-8")
    return status, json.loads(raw)


def cmd_status(_: argparse.Namespace) -> int:
    status, data = request_json("/status")
    print(json.dumps({"http_status": status, "body": data}, indent=2))
    return 0


def cmd_jurisdictions(args: argparse.Namespace) -> int:
    q: dict[str, str] = {}
    if args.state:
        q["state"] = args.state
    if args.cached is not None:
        q["cached"] = "true" if args.cached else "false"
    status, data = request_json("/jurisdictions", q or None)
    print(json.dumps({"http_status": status, "body": data}, indent=2))
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    q = {"q": args.query, "limit": str(args.limit)}
    path = f"/jurisdictions/{urllib.parse.quote(args.jurisdiction)}/search"
    status, data = request_json(path, q)
    print(json.dumps({"http_status": status, "body": data}, indent=2))
    return 0


def cmd_lookup(args: argparse.Namespace) -> int:
    q: dict[str, str] = {"state": args.state}
    if args.city:
        q["city"] = args.city
    if args.county:
        q["county"] = args.county
    if args.address:
        q["address"] = args.address
    status, data = request_json("/lookup", q)
    print(json.dumps({"http_status": status, "body": data}, indent=2))
    return 0


def cmd_code(args: argparse.Namespace) -> int:
    """GET /jurisdictions/:id/code/:path — path segments as on the site (e.g. chapter-5/article-i/section-sec.-5.1)."""
    jid = urllib.parse.quote(args.jurisdiction)
    segs = "/".join(urllib.parse.quote(s, safe="-._~") for s in args.path.strip("/").split("/"))
    path = f"/jurisdictions/{jid}/code/{segs}"
    status, data = request_json(path, None)
    print(json.dumps({"http_status": status, "body": data}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Open Legal Codes API client (see https://openlegalcodes.org/developers)")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("status", help="GET /status — health and cache stats")
    sp.set_defaults(func=cmd_status)

    jp = sub.add_parser("jurisdictions", help="GET /jurisdictions — list jurisdictions")
    jp.add_argument("--state", help="Filter by two-letter state, e.g. CA")
    jp.add_argument(
        "--cached",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Only jurisdictions that are cached (ready)",
    )
    jp.set_defaults(func=cmd_jurisdictions)

    sp2 = sub.add_parser("search", help="GET /jurisdictions/:id/search?q=…")
    sp2.add_argument("--jurisdiction", required=True, help="Jurisdiction id, e.g. ca-mountain-view")
    sp2.add_argument("--query", "-q", required=True, help="Search text")
    sp2.add_argument("--limit", type=int, default=5)
    sp2.set_defaults(func=cmd_search)

    lp = sub.add_parser("lookup", help="GET /lookup — find jurisdiction by city/county/address")
    lp.add_argument("--state", required=True)
    lp.add_argument("--city")
    lp.add_argument("--county")
    lp.add_argument("--address")
    lp.set_defaults(func=cmd_lookup)

    cp = sub.add_parser("code", help="GET /jurisdictions/:id/code/:path — section text")
    cp.add_argument("--jurisdiction", required=True)
    cp.add_argument(
        "--path",
        required=True,
        help="Code path after /code/, e.g. chapter-5/article-i/section-sec.-5.1",
    )
    cp.set_defaults(func=cmd_code)

    return p


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code} {e.reason}\n{body}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
