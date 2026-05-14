"""
HCDE 530 — MP1a CourtListener interactive charts (Plotly + Dash Mantine Components).

Data: week 6/Week6_files/courtlistener_week5_repull_40k.csv (~39k rows; cite metadata
      is non-zero only for W.D. Wash. rows in this pull).

Run interactively:
  week 6/.venv/bin/python "week 6/courtlistener_mp1a_dash.py"

Export static JPGs (same figures, ~45-point aggregates where noted):
  week 6/.venv/bin/python "week 6/courtlistener_mp1a_dash.py" --export
"""

from __future__ import annotations

import argparse
from pathlib import Path

import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "Week6_files" / "courtlistener_week5_repull_40k.csv"
EXPORT_DIR = HERE


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
    """One row per (year-month, court_id) with mean cite_count and n opinions — capped for display."""
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
    # keep most recent months if oversized
    if len(g) > max_points:
        g = g.sort_values("year_month").tail(max_points)
    g["court_code"] = g["court_id"].map({"washctapp": 0.0, "wawd": 1.0}).fillna(0.5)
    return g


def agg_judge_federal(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Judge-level stats — only federal rows have judge + non-flat cites in this pull."""
    d = df[(df["court_id"] == "wawd") & df["judge_clean"].notna()].copy()
    g = (
        d.groupby("judge_clean", as_index=False)
        .agg(
            opinion_count=("case", "count"),
            mean_cite_count=("cite_count", "mean"),
            total_cite_count=("cite_count", "sum"),
        )
        .sort_values("mean_cite_count", ascending=False)
        .head(top_n)
    )
    return g


def top_cases_by_jurisdiction(df: pd.DataFrame, court_id: str = "wawd", top_n: int = 45) -> pd.DataFrame:
    """Most cited *titles* in one jurisdiction (max cite_count per case title after dedupe)."""
    d = df[df["court_id"] == court_id].copy()
    # collapse duplicate rows sharing a case title — keep max cite_count observed
    g = d.groupby(["case", "court", "court_id"], as_index=False).agg(max_cite_count=("cite_count", "max"))
    g = g.sort_values("max_cite_count", ascending=False).head(top_n)
    return g


def fig_q1_scatter3d_monthly(df: pd.DataFrame) -> go.Figure:
    """
    (a) Citation intensity by court level over time — 3D scatter (~48 monthly buckets × courts).
    """
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


def fig_q2_bar_top_cases(df: pd.DataFrame) -> go.Figure:
    """
    (b) Most cited judgments in W.D. Wash. (specific jurisdiction) — horizontal bar, top 45 titles.
    """
    g = top_cases_by_jurisdiction(df, court_id="wawd", top_n=45)
    fig = px.bar(
        g.iloc[::-1],
        x="max_cite_count",
        y="case",
        orientation="h",
        color="max_cite_count",
        color_continuous_scale="Viridis",
        title=(
            "Most cited case titles in W.D. Wash. (max cite_count per title; "
            f"45 of {len(df[df['court_id']=='wawd']):,} federal rows)"
        ),
        labels={
            "max_cite_count": "Max cite_count in pull (dimensionless count)",
            "case": "Case title",
        },
    )
    fig.update_layout(
        coloraxis_showscale=True,
        coloraxis_colorbar_title="Max cite_count",
        yaxis=dict(tickfont=dict(size=9)),
        margin=dict(l=10, r=10, t=60, b=40),
    )
    return fig


def fig_q3_top_authorities(df: pd.DataFrame, top_n: int = 45) -> go.Figure:
    """
    (c) Case titles that accumulate the most incoming cite_count in this snapshot
    (proxy for 'most central' authorities in the pull), capped for display.
    """
    g = (
        df.groupby("case", as_index=False)
        .agg(total_cite_count=("cite_count", "sum"), opinion_rows=("cite_count", "count"))
        .sort_values("total_cite_count", ascending=False)
        .head(top_n)
    )
    mean_cite = float(df["cite_count"].mean())
    fig = px.bar(
        g.iloc[::-1],
        x="total_cite_count",
        y="case",
        orientation="h",
        color="opinion_rows",
        color_continuous_scale="Blues",
        title=(
            "Case titles with the highest summed cite_count across the dataset "
            f"(top {len(g)} titles; mean cite_count per opinion row = {mean_cite:.4f})"
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
        margin=dict(l=10, r=10, t=80, b=50),
    )
    return fig


def build_layout(fig1: go.Figure, fig2: go.Figure, fig3: go.Figure) -> dmc.MantineProvider:
    intro = dmc.Stack(
        [
            dmc.Title("CourtListener MP1a — three linked analytical views", order=2),
            dmc.Text(
                "Dataset: courtlistener_week5_repull_40k.csv — aggregated slices (~45–48 points) "
                "for performance; full table has 39,040 rows.",
                size="sm",
                c="dimmed",
            ),
            dmc.Alert(
                "Finding: cite_count is identically 0 for every Wash. Ct. App. (King County) row in "
                "this pull; all non-zero citation counts appear in the W.D. Wash. slice. "
                "Judge names are only populated for the federal rows (~2.9k opinions).",
                title="Coverage note",
                color="yellow",
            ),
        ],
        gap="sm",
        p="md",
    )

    grid = dmc.Stack(
        [
            dmc.SimpleGrid(
                cols={"base": 1, "lg": 2},
                spacing="md",
                children=[
                    dmc.Card(
                        [
                            dmc.CardSection(
                                dmc.Title("Question (a) — court level & time (3D)", order=4),
                                inheritPadding=True,
                                py="xs",
                            ),
                            dcc.Graph(id="fig-3d", figure=fig1, style={"height": "620px"}),
                        ],
                        withBorder=True,
                        shadow="sm",
                    ),
                    dmc.Card(
                        [
                            dmc.CardSection(
                                dmc.Title("Question (b) — jurisdiction spotlight", order=4),
                                inheritPadding=True,
                                py="xs",
                            ),
                            dcc.Graph(id="fig-bar", figure=fig2, style={"height": "720px"}),
                        ],
                        withBorder=True,
                        shadow="sm",
                    ),
                ],
            ),
            dmc.Card(
                [
                    dmc.CardSection(
                        dmc.Title("Question (c) — central case titles & averages", order=4),
                        inheritPadding=True,
                        py="xs",
                    ),
                    dcc.Graph(id="fig-authorities", figure=fig3, style={"height": "720px"}),
                ],
                withBorder=True,
                shadow="sm",
            ),
        ],
        gap="md",
    )

    stats = df_stats_block()

    return dmc.MantineProvider(
        dmc.Container(
            [intro, stats, grid],
            fluid=True,
            p="md",
        )
    )


def df_stats_block() -> dmc.Card:
    df = load_df()
    mean_all = float(df["cite_count"].mean())
    mean_wawd = float(df.loc[df["court_id"] == "wawd", "cite_count"].mean())
    mean_wash = float(df.loc[df["court_id"] == "washctapp", "cite_count"].mean())
    j = agg_judge_federal(df, top_n=5)
    judge_lines = [
        f"{row.judge_clean}: mean cite_count {row.mean_cite_count:.2f} across {int(row.opinion_count)} opinions"
        for row in j.itertuples()
    ]
    judge_text = (
        "Top federal judges by mean cite_count in this pull: " + " · ".join(judge_lines)
        if len(j)
        else "No judge strings available to rank."
    )
    return dmc.Card(
        [
            dmc.Title("Question (a) — judge / court-level narrative (tabular)", order=4),
            dmc.Text(
                "Wash. Ct. App. rows omit judge names and cite_count is uniformly 0 here, so judge-vs-court "
                "comparisons are only meaningful for the W.D. Wash. slice.",
                size="sm",
            ),
            dmc.Text(judge_text, size="sm"),
            dmc.Divider(my="sm"),
            dmc.Title("Question (c) — quick means", order=5),
            dmc.Text(
                f"Mean cite_count across all opinion rows: {mean_all:.4f}. "
                f"W.D. Wash. mean: {mean_wawd:.4f}; Wash. Ct. App. mean: {mean_wash:.4f}.",
                size="sm",
            ),
        ],
        withBorder=True,
        shadow="xs",
        p="md",
        mb="md",
    )


def export_jpgs(fig1: go.Figure, fig2: go.Figure, fig3: go.Figure) -> None:
    try:
        import kaleido  # noqa: F401
    except ImportError as e:  # pragma: no cover
        raise SystemExit("Install kaleido in the project venv to export JPGs.") from e

    paths = [
        (fig1, EXPORT_DIR / "mp1a_chart1_court_level_cites_3d.jpg"),
        (fig2, EXPORT_DIR / "mp1a_chart2_top_cited_cases_wd_wash.jpg"),
        (fig3, EXPORT_DIR / "mp1a_chart3_top_authority_titles.jpg"),
    ]
    for fig, path in paths:
        h = 900 if "chart2" in path.name or "chart3" in path.name else 820
        fig.write_image(str(path), format="jpg", scale=2, width=1280, height=h)
        print("wrote", path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", action="store_true", help="Write JPGs to week 6 folder and exit.")
    args = parser.parse_args()

    df = load_df()
    fig1 = fig_q1_scatter3d_monthly(df)
    fig2 = fig_q2_bar_top_cases(df)
    fig3 = fig_q3_top_authorities(df)

    if args.export:
        export_jpgs(fig1, fig2, fig3)
        return

    app = Dash(__name__)
    app.layout = build_layout(fig1, fig2, fig3)
    # Local dev server — bind 127.0.0.1
    app.run(debug=False, host="127.0.0.1", port=8050)


if __name__ == "__main__":
    main()
