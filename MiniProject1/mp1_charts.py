"""
HCDE 530 — Mini Project 1 chart helpers (standalone; no Dash dependency).

Data: MiniProject1/data/courtlistener.csv
Images: MiniProject1/images/mp1a_chart*.jpg
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "data" / "courtlistener.csv"
IMAGES_DIR = HERE / "images"

GRAPH_CONFIG = {
    "scrollZoom": True,
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d"],
}


def load_df() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df["date_of_decision"] = pd.to_datetime(df["date_of_decision"], errors="coerce")
    df["court_level"] = df["court_id"].map(
        {
            "washctapp": "State: Wash. Court of Appeals (King County pull)",
            "wawd": "Federal: U.S. District Court (W.D. Wash.)",
        }
    ).fillna(df["court_id"].astype(str))
    df["judge_clean"] = df["judge"].astype(str).str.strip()
    df.loc[df["judge_clean"].isin(["", "nan"]), "judge_clean"] = pd.NA
    return df


def agg_monthly_court_cites(df: pd.DataFrame, max_points: int = 48) -> pd.DataFrame:
    d = df.dropna(subset=["date_of_decision"]).copy()
    d["year_month"] = d["date_of_decision"].dt.to_period("M").dt.to_timestamp()
    g = (
        d.groupby(["year_month", "court_id", "court_level"], as_index=False)
        .agg(
            mean_cite_count=("cite_count", "mean"),
            opinion_count=("case", "count"),
        )
        .sort_values(["year_month", "court_id"])
    )
    if len(g) > max_points:
        g = g.sort_values("year_month").tail(max_points)
    g["court_code"] = g["court_id"].map({"washctapp": 0.0, "wawd": 1.0}).fillna(0.5)
    return g


def fig_q1_scatter3d_monthly(df: pd.DataFrame) -> go.Figure:
    g = agg_monthly_court_cites(df, max_points=48)
    fig = px.scatter_3d(
        g,
        x="year_month",
        y="court_code",
        z="mean_cite_count",
        color="court_level",
        size="opinion_count",
        size_max=40,
        hover_data={
            "court_id": True,
            "mean_cite_count": ":.3f",
            "opinion_count": True,
            "court_code": False,
        },
        title=(
            "Mean incoming citations per opinion by month and court level "
            f"(aggregated; up to {len(g)} points from {len(df):,} rows)"
        ),
    )
    fig.update_layout(
        scene=dict(
            xaxis_title="Month (decision date)",
            yaxis_title="Court id (0 = washctapp, 1 = wawd)",
            zaxis_title="Mean cite_count (incoming cites / opinion in window)",
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        legend_title_text="Court level",
    )
    return fig


def _q2_case_frame(
    df: pd.DataFrame, *, court_id: str, top_n: int, rank_mode: str
) -> tuple[pd.DataFrame, str, int, str, str]:
    top_n = int(max(5, min(60, top_n)))
    d = df[df["court_id"] == court_id].copy()
    rows_in_court = len(d)
    court_map = df.drop_duplicates("court_id").set_index("court_id")["court"]
    court_label = str(court_map[court_id]) if court_id in court_map.index else str(court_id)
    if rows_in_court == 0:
        return pd.DataFrame(), court_label, 0, "", ""
    if rank_mode == "mean":
        g = (
            d.groupby(["case", "court", "court_id"], as_index=False)
            .agg(cite_value=("cite_count", "mean"), opinion_rows=("cite_count", "count"))
            .sort_values("cite_value", ascending=False)
            .head(top_n)
        )
        metric_label = "Mean cite_count (per row, per title)"
    else:
        g = (
            d.groupby(["case", "court", "court_id"], as_index=False)
            .agg(cite_value=("cite_count", "max"), opinion_rows=("cite_count", "count"))
            .sort_values("cite_value", ascending=False)
            .head(top_n)
        )
        metric_label = "Max cite_count (per title in pull)"
    g = g.reset_index(drop=True)
    g["rank_1based"] = (g.index + 1).astype(int)
    return g, court_label, rows_in_court, metric_label, rank_mode


def fig_q2_scatter3d_jurisdiction(
    df: pd.DataFrame,
    *,
    court_id: str = "wawd",
    top_n: int = 45,
    rank_mode: str = "max",
) -> go.Figure:
    mode = rank_mode if rank_mode in ("mean", "max") else "max"
    g, court_label, rows_in_court, metric_label, _ = _q2_case_frame(
        df, court_id=court_id, top_n=top_n, rank_mode=mode
    )
    if len(g) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No case titles in this court slice.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        fig.update_layout(title="Question (b) — no rows to plot")
        return fig
    fig = px.scatter_3d(
        g,
        x="rank_1based",
        y="cite_value",
        z="opinion_rows",
        color="cite_value",
        size="opinion_rows",
        size_max=55,
        hover_name="case",
        hover_data={
            "case": False,
            "cite_value": ":.3f",
            "opinion_rows": True,
            "rank_1based": True,
            "court_id": True,
        },
        color_continuous_scale="Viridis",
        title=(
            f"3D — most cited case titles — {court_label} — by {mode} cite (top {len(g)} titles; "
            f"{rows_in_court:,} rows in slice; {len(df):,} in CSV)"
        ),
    )
    fig.update_layout(
        scene=dict(
            xaxis_title="Rank in slice (1 = highest metric)",
            yaxis_title=metric_label,
            zaxis_title="Opinion rows for this title (duplicate rows in pull)",
            bgcolor="rgb(248,249,252)",
            xaxis=dict(backgroundcolor="rgb(248,249,252)"),
            yaxis=dict(backgroundcolor="rgb(248,249,252)"),
            zaxis=dict(backgroundcolor="rgb(248,249,252)"),
        ),
        margin=dict(l=0, r=0, t=70, b=0),
        coloraxis_colorbar_title="Cite metric",
    )
    return fig


def fig_q3_top_authorities(df: pd.DataFrame, top_n: int = 45, min_opinion_rows: int = 1) -> go.Figure:
    top_n = int(max(5, min(60, top_n)))
    min_opinion_rows = int(max(1, min(200, min_opinion_rows)))
    g = (
        df.groupby("case", as_index=False)
        .agg(total_cite_count=("cite_count", "sum"), opinion_rows=("cite_count", "count"))
        .query("opinion_rows >= @min_opinion_rows")
        .sort_values("total_cite_count", ascending=False)
        .head(top_n)
    )
    mean_cite = float(df["cite_count"].mean())
    if len(g) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No titles meet min_opinion_rows at this setting.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        fig.update_layout(title="Question (c) — no rows to plot")
        return fig
    fig = px.bar(
        g.iloc[::-1],
        x="total_cite_count",
        y="case",
        orientation="h",
        color="opinion_rows",
        color_continuous_scale="Blues",
        title=(
            "Case titles with the highest summed cite_count across the dataset "
            f"(top {len(g)} titles with ≥{min_opinion_rows} row(s) per title; "
            f"mean cite_count per opinion row = {mean_cite:.4f})"
        ),
        labels={
            "total_cite_count": "Sum of cite_count (clusters summed across duplicate rows)",
            "case": "Case title",
            "opinion_rows": "Rows in pull for this title",
        },
    )
    fig.update_layout(
        coloraxis_colorbar_title="Opinion rows",
        yaxis=dict(tickfont=dict(size=8)),
        margin=dict(l=10, r=10, t=90, b=50),
    )
    return fig


def export_chart_images(
    fig1: go.Figure,
    fig2: go.Figure,
    fig3: go.Figure,
    out_dir: Path | None = None,
) -> list[Path]:
    try:
        import kaleido  # noqa: F401
    except ImportError as e:
        raise ImportError("Install kaleido: pip install kaleido") from e

    out_dir = out_dir or IMAGES_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        (fig1, out_dir / "mp1a_chart1_court_level_cites_3d.jpg", 820),
        (fig2, out_dir / "mp1a_chart2_top_cited_cases_wd_wash.jpg", 900),
        (fig3, out_dir / "mp1a_chart3_top_authority_titles.jpg", 900),
    ]
    written: list[Path] = []
    for fig, path, height in paths:
        fig.write_image(str(path), format="jpg", scale=2, width=1280, height=height)
        written.append(path)
        print("wrote", path)
    return written


if __name__ == "__main__":
    df = load_df()
    export_chart_images(
        fig_q1_scatter3d_monthly(df),
        fig_q2_scatter3d_jurisdiction(df, court_id="wawd", top_n=45, rank_mode="max"),
        fig_q3_top_authorities(df, top_n=45, min_opinion_rows=1),
    )
