#!/usr/bin/env python3
"""
HCDE 530 — Week 4 assignment: call a real public API (not the class demo API).

Uses the official CourtListener Python client (wraps REST v4):
  https://pypi.org/project/courtlistener-api-client/

Citation lookup docs: https://www.courtlistener.com/help/api/rest/citation-lookup/

Install once into your global interpreter (same env as your Jupyter kernel):
  python3 -m pip install -r "week 4/requirements.txt"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from courtlistener import CourtListener  # type: ignore[import-untyped]
except ModuleNotFoundError:
    print(
        "Missing package `courtlistener-api-client`.\n"
        '  python3 -m pip install -r "week 4/requirements.txt"\n'
        "Use the same Python as your Jupyter kernel (global interpreter).",
        file=sys.stderr,
    )
    raise SystemExit(1) from None

HERE = Path(__file__).resolve().parent

# Env var for the API token (CourtListener account → API). Put in `week 4/.env`.
TOKEN_ENV = "COURTLISTENER_API_TOKEN"


def load_dotenv_file(path: Path) -> None:
    """Merge KEY=value lines from `.env` into os.environ (no extra pip deps).

    Accepts ``KEY=value``, ``export KEY=value``, and quoted values.
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
        if key.lower().startswith("export "):
            key = key[7:].strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def run_citation_demo(client: CourtListener) -> None:
    """POST citation-lookup via SDK (`client.citation_lookup.lookup_text`)."""
    sample_text = (
        "Obergefell v. Hodges (576 U.S. 644) established the right to marriage "
        "among same-sex couples."
    )
    print("Citation lookup — sample text:\n")
    print(f"  {sample_text}\n")

    # SDK sends the same form-encoded POST as the REST docs; returns list[dict].
    results = client.citation_lookup.lookup_text(sample_text)

    rows: list[dict[str, object]] = []
    for idx, item in enumerate(results, start=1):
        citation = item.get("citation", "")
        normalized = item.get("normalized_citations") or []
        status = item.get("status")
        err = item.get("error_message", "")
        start_i = item.get("start_index")
        end_i = item.get("end_index")

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

        rows.append(
            {
                "citation": citation,
                "http_status": status,
                "case_name": first_case or None,
            }
        )

    out_path = HERE / "week4_citation_lookup_sample.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Saved raw API response list to {out_path.name}")

    summary_path = HERE / "week4_citation_extracted.tsv"
    with summary_path.open("w", encoding="utf-8", newline="") as f:
        f.write("citation\thttp_status\tcase_name\n")
        for row in rows:
            cn = row["case_name"] if row["case_name"] is not None else ""
            f.write(f"{row['citation']}\t{row['http_status']}\t{cn}\n")
    print(f"Saved three-field extract (TSV) to {summary_path.name}")
    print("\nExtracted fields (3+): citation, http_status, case_name")


def run_rest_examples(client: CourtListener) -> None:
    """
    Patterns from the CourtListener client README: opinions + dockets.

    Dockets show two pagination styles:
    - Iterate the ResourceIterator: walks every page until exhaustion.
    - Manual: ``results.results``, ``results.has_next()``, ``results.next()``.
    """
    # Get a specific opinion by ID (REST: GET /opinions/{id}/).
    opinion = client.opinions.get(1)
    print("--- opinions.get(1) ---")
    print(f"  keys: {sorted(opinion.keys())[:12]} ... ({len(opinion)} fields total)")
    for key in ("id", "absolute_url", "cluster"):
        if key in opinion:
            print(f"  {key}: {opinion[key]!r}")

    # Search opinions (filters are passed as keyword args to .list()).
    response = client.opinions.list(cluster__case_name="Miranda")
    print("\n--- opinions.list(cluster__case_name='Miranda') ---")
    print(f"  count (total matches): {response.count}")
    print("  first page results (up to 3):")
    for i, op in enumerate(response.results):
        if i >= 3:
            break
        print(f"    [{i}] opinion id={op.get('id')} cluster={op.get('cluster')}")

    # Dockets (SCOTUS): ResourceIterator yields every row across all pages.
    results = client.dockets.list(court="scotus")
    print("\n--- dockets.list(court='scotus') — iterate all pages ---")
    print("  (Cap at 5 rows here; delete the `if n >= 5` break to print everything.)")
    for n, docket in enumerate(results):
        if n >= 5:
            break
        sid = docket.get("id")
        name = docket.get("case_name_short") or docket.get("case_name")
        print(f"  [{n}] id={sid}  {name!r}")

    # Same query fresh: navigate pages manually instead of the for-loop.
    print("\n--- dockets.list(court='scotus') — manual page navigation ---")
    page = client.dockets.list(court="scotus")
    # Current page rows (list of dicts).
    print(f"  results.results (page 1): {len(page.results)} dockets")
    if page.results:
        d0 = page.results[0]
        print(f"  first row sample: id={d0.get('id')} case_name_short={d0.get('case_name_short')!r}")

    if page.has_next():
        page.next()
        print(f"  after page.next(): {len(page.results)} dockets on page 2")
        if page.results:
            d0 = page.results[0]
            print(f"  first row on page 2: id={d0.get('id')}")
    else:
        print("  page.has_next() is False — no second page for this filter.")


def main() -> None:
    load_dotenv_file(HERE / ".env")
    token = os.environ.get(TOKEN_ENV)
    if not token:
        print(
            f"Missing {TOKEN_ENV}. Add to `week 4/.env`:\n"
            f"  {TOKEN_ENV}=your_courtlistener_token\n"
            "Do not commit `.env`."
        )
        raise SystemExit(1)

    parser = argparse.ArgumentParser(description="CourtListener API — Week 4")
    parser.add_argument(
        "--examples",
        action="store_true",
        help="Run opinions/docket demo (README-style), not citation lookup.",
    )
    args = parser.parse_args()

    # Context manager closes the underlying httpx client when done.
    with CourtListener(api_token=token) as client:
        if args.examples:
            run_rest_examples(client)
        else:
            run_citation_demo(client)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # httpx errors from the SDK surface here; keep message readable.
        print(f"Request or API error: {e}", file=sys.stderr)
        raise SystemExit(1) from e
