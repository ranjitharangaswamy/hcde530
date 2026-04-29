#!/usr/bin/env python3
"""
HCDE 530 — Week 4 assignment: call a real public API (not the class demo API).

CourtListener Citation Lookup & Verification API (POST, token auth).
Docs: https://www.courtlistener.com/help/api/rest/citation-lookup/
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Endpoint from CourtListener docs — parses citations (Eyecite) and matches DB clusters.
CITATION_LOOKUP_URL = "https://www.courtlistener.com/api/rest/v4/citation-lookup/"

# Env var name for the API token (create account on CourtListener → API token).
# Put `COURTLISTENER_API_TOKEN=...` in `week 4/.env` — never commit that file.
TOKEN_ENV = "COURTLISTENER_API_TOKEN"


def load_dotenv_file(path: Path) -> None:
    """
    Minimal `.env` loader (no pip dependency). Lines like KEY=value become os.environ.

    Matches the course pattern: secrets live beside the script, loaded before
    os.environ.get(...) reads them.
    """
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def citation_lookup(text: str, token: str) -> list[dict]:
    """
    POST form field `text=` — the API scans the blob, returns a JSON list (one dict per hit).

    Each dict includes citation string, indices in the input, HTTP-style status,
    error_message, and `clusters` (matched opinions). See field definitions in the docs.
    """
    body = urllib.parse.urlencode({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        CITATION_LOOKUP_URL,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            # CourtListener uses "Authorization: Token <secret>" (not Bearer).
            "Authorization": f"Token {token}",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
    parsed = json.loads(raw)
    # Empty input with no citations returns [] per docs; otherwise list of citation objects.
    return parsed if isinstance(parsed, list) else []


def main() -> None:
    # Load `week 4/.env` into the process environment, then read the token safely.
    load_dotenv_file(HERE / ".env")
    token = os.environ.get(TOKEN_ENV)
    if not token:
        print(
            f"Missing {TOKEN_ENV}. Create a file named `.env` in this folder with:\n"
            f"  {TOKEN_ENV}=your_courtlistener_token\n"
            "Get a token from CourtListener (account → API). Do not commit `.env`."
        )
        raise SystemExit(1)

    # Example from the public docs — well-known cite + short sentence for readable output.
    sample_text = (
        "Obergefell v. Hodges (576 U.S. 644) established the right to marriage "
        "among same-sex couples."
    )
    print("POST citation-lookup with sample text:\n")
    print(f"  {sample_text}\n")

    results = citation_lookup(sample_text, token)

    for idx, item in enumerate(results, start=1):
        # Extract several top-level fields the API documents explicitly.
        citation = item.get("citation", "")
        # normalized_citations catches typos / non-canonical reporters (e.g. "US" → "U.S.").
        normalized = item.get("normalized_citations") or []
        # status mirrors HTTP semantics: 200 OK, 404 not in DB, 300 ambiguous, etc.
        status = item.get("status")
        # error_message explains failures when status is not 200.
        err = item.get("error_message", "")
        # Character span in the submitted `text` — useful for highlighting in a UI.
        start_i = item.get("start_index")
        end_i = item.get("end_index")

        # Pull at least one nested field from clusters (first match) when present.
        clusters = item.get("clusters") or []
        first_case = ""
        if clusters and isinstance(clusters[0], dict):
            first_case = str(clusters[0].get("case_name", "")).strip()

        print(f"--- Citation hit {idx} ---")
        print(f"  citation:              {citation}")
        print(f"  normalized_citations:  {normalized}")
        print(f"  status:                {status}")
        print(f"  error_message:         {err!r}")
        print(f"  start_index / end:     {start_i} .. {end_i}")
        if first_case:
            print(f"  first cluster case_name: {first_case}")
        print(f"  cluster count:         {len(clusters)}")
        print()

    out_path = HERE / "week4_citation_lookup_sample.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Saved raw API response list to {out_path.name}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code} {e.reason}\n{detail}")
    except urllib.error.URLError as e:
        print(f"Request failed: {e}")
