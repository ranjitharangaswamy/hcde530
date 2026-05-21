"""Load the local CourtListener CSV export (no API calls)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

SEATTLE_JURISDICTION_LABEL = "Seattle jurisdiction"


def find_courtlistener_csv() -> Path:
    """Resolve courtlistener.csv whether cwd is repo root, week 5/6, or MiniProject1."""
    here = Path.cwd().resolve()
    candidates: list[Path] = []
    for base in [here, *here.parents]:
        candidates.extend(
            [
                base / "MiniProject1" / "data" / "courtlistener.csv",
                base / "week 6" / "Week6_files" / "courtlistener_week5_repull_40k.csv",
                base / "Week6_files" / "courtlistener_week5_repull_40k.csv",
                base / "data" / "courtlistener.csv",
                base / "courtlistener_week5_repull_40k.csv",
            ]
        )
    seen: set[Path] = set()
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        if path.is_file():
            return path
    raise FileNotFoundError(
        "Could not find courtlistener CSV. Expected MiniProject1/data/courtlistener.csv "
        "or week 6/Week6_files/courtlistener_week5_repull_40k.csv"
    )


def load_courtlistener_csv() -> pd.DataFrame:
    path = find_courtlistener_csv()
    df = pd.read_csv(path)
    df["date_of_decision"] = pd.to_datetime(df["date_of_decision"], errors="coerce")
    print(f"Loaded {len(df):,} rows from {path}")
    return df


def split_parties(case_name: str) -> tuple[str, str]:
    if not case_name or not isinstance(case_name, str):
        return "", ""
    for sep in (" v. ", " V. ", " vs. ", " VS. ", " v ", " V "):
        if sep in case_name:
            left, right = case_name.split(sep, 1)
            return left.strip(), right.strip()
    return "", ""


def slice_sample_opinions(df: pd.DataFrame, n: int = 25) -> pd.DataFrame:
    """Sample rows with parseable party names (replaces Miranda API search on local CSV)."""
    mask = df["case"].astype(str).str.contains(r"\s+v\.?\s+", case=False, regex=True, na=False)
    out = df.loc[mask].head(n).copy()
    if len(out) < n:
        out = df.head(n).copy()
    return out


def slice_seattle_federal(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    d = df[df["court_id"] == "wawd"].copy()
    return d.head(n)


def slice_king_county_recent(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    d = df[df["court_id"] == "washctapp"].copy()
    d = d.sort_values("date_of_decision", ascending=False)
    return d.head(n)
