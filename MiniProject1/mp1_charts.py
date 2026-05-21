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

GALLERY_TEMPLATE = "plotly_white"
GALLERY_COLOR_SCALE = "Viridis"
GALLERY_TREEMAP_SCALE = "Turbo"
COURT_LINE_COLORS = {
    "Federal: U.S. District Court (W.D. Wash.)": "#7C3AED",
    "State: Wash. Court of Appeals (King County pull)": "#F97316",
}


def apply_gallery_theme(fig: go.Figure) -> go.Figure:
    """Polished defaults inspired by Plotly Dash gallery apps."""
    fig.update_layout(
        template=GALLERY_TEMPLATE,
        font=dict(family="Inter, system-ui, sans-serif", size=13),
        title=dict(font=dict(size=16)),
        hoverlabel=dict(bgcolor="white", font_size=12),
        margin=dict(l=48, r=24, t=72, b=48),
        paper_bgcolor="rgb(248,249,252)",
        plot_bgcolor="rgb(255,255,255)",
    )
    return fig


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


def agg_judge_federal(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    d = df[(df["court_id"] == "wawd") & df["judge_clean"].notna()].copy()
    return (
        d.groupby("judge_clean", as_index=False)
        .agg(
            opinion_count=("case", "count"),
            mean_cite_count=("cite_count", "mean"),
            total_cite_count=("cite_count", "sum"),
        )
        .sort_values("mean_cite_count", ascending=False)
        .head(int(max(1, top_n)))
    )


def fig_q1_scatter3d_monthly(df: pd.DataFrame) -> go.Figure:
    """Question (a): line + markers — mean cites over time by court level (readable vs 3D)."""
    g = agg_monthly_court_cites(df, max_points=48)
    fig = px.line(
        g,
        x="year_month",
        y="mean_cite_count",
        color="court_level",
        color_discrete_map=COURT_LINE_COLORS,
        line_shape="linear",
        markers=True,
        hover_data={
            "court_id": True,
            "mean_cite_count": ":.3f",
            "opinion_count": True,
            "court_level": False,
        },
        title=(
            "Federal mean cites rise over time while state means stay at zero "
            f"(monthly buckets; {len(g)} points from {len(df):,} rows)"
        ),
        labels={
            "year_month": "Month (decision date)",
            "mean_cite_count": "Mean cite_count per opinion row",
            "court_level": "Court level",
            "opinion_count": "Opinions in bucket",
        },
    )
    fig.update_traces(
        mode="lines+markers",
        marker=dict(size=10, line=dict(width=1, color="white")),
        line=dict(width=3),
    )
    fig.update_layout(
        xaxis_title="Month (decision date)",
        yaxis_title="Mean cite_count (incoming cites / opinion in bucket)",
        legend_title_text="Court level",
        hovermode="x unified",
        uirevision="mp1-q1",
    )
    return apply_gallery_theme(fig)


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
        color_continuous_scale=GALLERY_COLOR_SCALE,
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
        uirevision="mp1-q2",
    )
    return apply_gallery_theme(fig)


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
    g = g.copy()
    g["root"] = "Citation mass (top titles)"
    cite_min, cite_max = int(g["total_cite_count"].min()), int(g["total_cite_count"].max())
    fig = px.treemap(
        g,
        path=["root", "case"],
        values="total_cite_count",
        color="total_cite_count",
        color_continuous_scale=GALLERY_TREEMAP_SCALE,
        range_color=[cite_min, cite_max],
        custom_data=["opinion_rows"],
        title=(
            "Most citation mass concentrates in a few case titles "
            f"(treemap: top {len(g)} with ≥{min_opinion_rows} row(s)/title; "
            f"mean cite_count per row = {mean_cite:.4f}; {len(df):,} rows total)"
        ),
    )
    fig.update_traces(
        textinfo="label+value",
        texttemplate="%{label}<br>%{value:,.0f} cites",
        textfont=dict(size=11, color="white"),
        marker=dict(line=dict(width=1.5, color="rgba(255,255,255,0.85)")),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Sum cite_count=%{value:,.0f}<br>"
            "Opinion rows=%{customdata[0]}<extra></extra>"
        ),
    )
    fig.update_layout(
        coloraxis_colorbar_title="Sum cite_count",
        margin=dict(l=10, r=10, t=90, b=10),
        uirevision="mp1-q3",
    )
    return apply_gallery_theme(fig)


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
        (fig1, out_dir / "mp1a_chart1_court_level_over_time.jpg", 820),
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
