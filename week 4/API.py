"""
HCDE 530 Week 4 — pull review data from the class API (category + helpful votes).

The API does not expose reviewer IDs. This script writes average star rating
per reviewed product (`app`) — one row per app — as a stand-in for “per user”
ratings of each tool.
"""

import csv
import json
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "https://hcde530-week4-api.onrender.com"
REVIEWS_URL = f"{BASE_URL}/reviews"

HERE = Path(__file__).resolve().parent


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def main() -> None:
    root = fetch_json(BASE_URL)
    print(f"API: {root.get('name', 'unknown')}\n")

    data = fetch_json(f"{REVIEWS_URL}?limit=500")
    reviews = data.get("reviews", [])

    rows: list[dict[str, object]] = []
    for item in reviews:
        category = item.get("category", "")
        helpful = item.get("helpful_votes", 0)
        print(f"{category} — {helpful} helpful votes")
        rows.append({"category": category, "helpful_votes": helpful})

    out_path = HERE / "reviews_category_helpful.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "helpful_votes"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {len(rows)} rows to {out_path.name}")

    # Average rating per reviewed app (no per-reviewer ID in API).
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for item in reviews:
        app = str(item.get("app", "")).strip()
        if not app:
            continue
        rating = int(item.get("rating") or 0)
        sums[app] = sums.get(app, 0.0) + rating
        counts[app] = counts.get(app, 0) + 1

    avg_rows: list[dict[str, object]] = []
    for app in sorted(counts):
        n = counts[app]
        avg = sums[app] / n if n else 0.0
        avg_rows.append(
            {
                "app": app,
                "average_rating": round(avg, 2),
                "review_count": n,
            }
        )

    avg_path = HERE / "average_rating_per_user.csv"
    with avg_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["app", "average_rating", "review_count"])
        writer.writeheader()
        writer.writerows(avg_rows)
    print(f"Wrote {len(avg_rows)} rows to {avg_path.name} (mean stars, grouped by app)")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as e:
        print(f"Request failed: {e}")
