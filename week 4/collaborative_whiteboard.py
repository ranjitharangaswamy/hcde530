"""
Filter Week 4 API reviews to category "collaborative whiteboard",
save a CSV, and render a bar chart (SVG, no extra dependencies).
"""

from __future__ import annotations

import csv
import json
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

BASE_URL = "https://hcde530-week4-api.onrender.com"
REVIEWS_URL = f"{BASE_URL}/reviews"
CATEGORY = "collaborative whiteboard"

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "collaborative_whiteboard_reviews.csv"
CHART_PATH = HERE / "collaborative_whiteboard_ratings.svg"


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def rating_counts(reviews: list[dict]) -> dict[int, int]:
    c: Counter[int] = Counter()
    for r in reviews:
        rating = int(r.get("rating", 0))
        if 1 <= rating <= 5:
            c[rating] += 1
    return {stars: c.get(stars, 0) for stars in range(1, 6)}


def build_bar_chart_svg(counts: dict[int, int], title: str) -> str:
    w, h = 640, 420
    margin_l, margin_r, margin_t, margin_b = 72, 40, 56, 80
    inner_w = w - margin_l - margin_r
    inner_h = h - margin_t - margin_b
    max_c = max(counts.values()) or 1
    n = len(counts)
    gap = 16
    bar_w = (inner_w - gap * (n - 1)) / n

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="system-ui, sans-serif">',
        f'<rect width="100%" height="100%" fill="#fafafa"/>',
        f'<text x="{w / 2}" y="{margin_t - 18}" text-anchor="middle" '
        f'font-size="18" font-weight="600" fill="#111">{title}</text>',
        f'<line x1="{margin_l}" y1="{margin_t + inner_h}" x2="{w - margin_r}" '
        f'y2="{margin_t + inner_h}" stroke="#ccc" stroke-width="1"/>',
    ]

    x = margin_l
    baseline = margin_t + inner_h
    for stars in range(1, 6):
        c = counts[stars]
        bar_h = inner_h * (c / max_c) if max_c else 0
        y = baseline - bar_h
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_w:.1f}" height="{max(bar_h, 0):.1f}" '
            f'rx="6" fill="#2563eb" opacity="0.9"/>'
        )
        parts.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{baseline + 28}" text-anchor="middle" '
            f'font-size="14" fill="#333">{stars}★</text>'
        )
        parts.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{y - 8:.1f}" text-anchor="middle" '
            f'font-size="13" font-weight="600" fill="#111">{c}</text>'
        )
        x += bar_w + gap

    parts.append(
        f'<text x="{margin_l}" y="{h - 24}" font-size="12" fill="#666">'
        f"Reviews in category: {sum(counts.values())}</text>"
    )
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    fetch_json(BASE_URL)
    data = fetch_json(f"{REVIEWS_URL}?limit=500")
    all_reviews: list[dict] = data.get("reviews", [])
    filtered = [r for r in all_reviews if r.get("category") == CATEGORY]

    fieldnames = [
        "id",
        "app",
        "category",
        "rating",
        "helpful_votes",
        "date",
        "verified_purchase",
        "review",
    ]
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in filtered:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    counts = rating_counts(filtered)
    svg = build_bar_chart_svg(
        counts,
        "Collaborative whiteboard — reviews by star rating",
    )
    CHART_PATH.write_text(svg, encoding="utf-8")

    print(f"Wrote {len(filtered)} rows to {CSV_PATH.name}")
    print(f"Bar chart saved to {CHART_PATH.name} (open in a browser)")
    print("Rating counts:", counts)


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as e:
        print(f"Request failed: {e}")
