"""
HCDE 530 — MP1a CourtListener interactive charts (Plotly + Dash Mantine Components).

Data: week 6/Week6_files/courtlistener_week5_repull_40k.csv (~39k rows; cite metadata
      is non-zero only for W.D. Wash. rows in this pull).

Run interactively:
  week 6/.venv/bin/python "week 6/courtlistener_mp1a_dash.py"

Export static JPGs (same figures, ~45-point aggregates where noted). **Note:** JPGs are
      snapshots — chart (b) is a **3D** view in the live Dash app; the export is a frozen angle.
  week 6/.venv/bin/python "week 6/courtlistener_mp1a_dash.py" --export
"""

from __future__ import annotations

import argparse
from pathlib import Path

import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc

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


def _q2_case_frame(
    df: pd.DataFrame, *, court_id: str, top_n: int, rank_mode: str
) -> tuple[pd.DataFrame, str, int, str, str]:
    """Build one tidy frame for Q(b) 3D: rank, cite metric, opinion row count per title."""
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
    """
    (b) Most cited judgments in a jurisdiction — 3D scatter (interactive rotate/zoom in browser).
    Axes: rank (1 = strongest in slice) × cite metric × how many duplicate rows exist for that title.
    """
    mode = rank_mode if rank_mode in ("mean", "max") else "max"
    g, court_label, rows_in_court, metric_label, _ = _q2_case_frame(df, court_id=court_id, top_n=top_n, rank_mode=mode)
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
    """
    (c) Case titles that accumulate the most incoming cite_count in this snapshot
    (proxy for 'most central' authorities in the pull), capped for display.
    """
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
            text="No titles meet min_opinion_rows at this setting — loosen the Mantine slider.",
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
        dragmode="select",
        clickmode="event+select",
    )
    fig.update_traces(selected_marker_opacity=0.85, unselected_marker_opacity=0.35)
    return fig


_GRAPH_CONFIG = {
    "scrollZoom": True,
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d"],
}


def _court_select_data() -> list[dict[str, str]]:
    return [
        {"value": "wawd", "label": "Federal — W.D. Wash. (wawd)"},
        {"value": "washctapp", "label": "State — Wash. Ct. App. / King County pull (washctapp)"},
    ]


def _slider_marks(min_v: int, max_v: int, step: int) -> list[dict]:
    return [{"value": v, "label": str(v)} for v in range(min_v, max_v + 1, step)]


def _q2_default_badges() -> list:
    return [
        dmc.Badge("court=wawd", variant="light", color="violet"),
        dmc.Badge("rank=max", variant="light", color="gray"),
        dmc.Badge("top_n=45", variant="outline", color="violet"),
    ]


def build_layout(df: pd.DataFrame, fig1: go.Figure) -> dmc.MantineProvider:
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
                            dcc.Graph(
                                id="fig-3d",
                                figure=fig1,
                                style={"height": "620px"},
                                config=_GRAPH_CONFIG,
                            ),
                        ],
                        withBorder=True,
                        shadow="sm",
                    ),
                    dmc.Card(
                        withBorder=True,
                        shadow="md",
                        radius="md",
                        children=[
                            dmc.CardSection(
                                dmc.Group(
                                    [
                                        dmc.RingProgress(
                                            sections=[{"value": 100, "color": "violet"}],
                                            size=52,
                                            thickness=6,
                                            label=dmc.Center(
                                                dmc.Text("b", size="xs", fw=800, c="violet"),
                                                style={"height": "100%"},
                                            ),
                                        ),
                                        dmc.Stack(
                                            [
                                                dmc.Group(
                                                    [
                                                        dmc.Title(
                                                            "Question (b) — jurisdiction spotlight",
                                                            order=4,
                                                            mb=0,
                                                        ),
                                                        dmc.Badge("3D", variant="filled", color="violet"),
                                                        dmc.Badge(
                                                            "Mantine + Plotly",
                                                            variant="light",
                                                            color="gray",
                                                        ),
                                                    ],
                                                    gap="xs",
                                                    align="flex-end",
                                                ),
                                                dmc.Text(
                                                    "Rotate and zoom the scene; use the controls to "
                                                    "change court, ranking mode, and how many titles load.",
                                                    size="sm",
                                                    c="dimmed",
                                                ),
                                            ],
                                            gap=4,
                                            style={"flex": 1},
                                        ),
                                    ],
                                    align="flex-start",
                                    gap="md",
                                    wrap="nowrap",
                                ),
                                inheritPadding=True,
                                py="md",
                                withBorder=True,
                            ),
                            dmc.CardSection(
                                [
                                    dmc.Alert(
                                        "Tip: drag the plot background to orbit. Scroll to zoom. "
                                        "Each point is one case title; size shows how many CSV rows share that title.",
                                        title="Reading this 3D view",
                                        color="blue",
                                        variant="light",
                                        mb="sm",
                                    ),
                                    dmc.Paper(
                                        p="md",
                                        radius="sm",
                                        withBorder=True,
                                        bg="var(--mantine-color-gray-0)",
                                        children=[
                                            dmc.Group(
                                                [
                                                    dmc.Text("Active filters", size="xs", tt="uppercase", fw=700, c="dimmed"),
                                                    dmc.Group(id="q2-filter-badges", gap="xs", children=_q2_default_badges()),
                                                ],
                                                justify="space-between",
                                                align="center",
                                                wrap="wrap",
                                                mb="sm",
                                            ),
                                            dmc.SimpleGrid(
                                                cols={"base": 1, "sm": 2},
                                                spacing="md",
                                                children=[
                                                    dmc.Stack(
                                                        [
                                                            dmc.Text("Jurisdiction", size="sm", fw=600),
                                                            dmc.Tooltip(
                                                                label="Switches pandas slice by court_id before the 3D aggregation.",
                                                                position="top",
                                                                withArrow=True,
                                                                children=dmc.Select(
                                                                    id="q2-court",
                                                                    data=_court_select_data(),
                                                                    value="wawd",
                                                                    searchable=True,
                                                                    clearable=False,
                                                                    w="100%",
                                                                ),
                                                            ),
                                                        ],
                                                        gap=6,
                                                    ),
                                                    dmc.Stack(
                                                        [
                                                            dmc.Text("Rank case titles by", size="sm", fw=600),
                                                            dmc.Tooltip(
                                                                label="Max = strongest single-row cite_count for that title. "
                                                                "Mean = average cite_count across rows with that title.",
                                                                position="top",
                                                                withArrow=True,
                                                                children=dmc.SegmentedControl(
                                                                    id="q2-rank-mode",
                                                                    data=[
                                                                        {"value": "max", "label": "Max cite / title"},
                                                                        {"value": "mean", "label": "Mean cite / title"},
                                                                    ],
                                                                    value="max",
                                                                    fullWidth=True,
                                                                    color="violet",
                                                                ),
                                                            ),
                                                        ],
                                                        gap=6,
                                                    ),
                                                ],
                                            ),
                                            dmc.Stack(
                                                [
                                                    dmc.Text("How many titles to show", size="sm", fw=600),
                                                    dmc.Slider(
                                                        id="q2-top-n",
                                                        min=10,
                                                        max=50,
                                                        step=5,
                                                        value=45,
                                                        marks=_slider_marks(10, 50, 10),
                                                        color="violet",
                                                    ),
                                                    dmc.Text(id="q2-summary", size="sm", c="dimmed"),
                                                ],
                                                gap=6,
                                                mt="sm",
                                            ),
                                        ],
                                    ),
                                    dcc.Graph(
                                        id="fig-q2-3d",
                                        figure=fig_q2_scatter3d_jurisdiction(
                                            df, court_id="wawd", top_n=45, rank_mode="max"
                                        ),
                                        style={"height": "700px"},
                                        config=_GRAPH_CONFIG,
                                    ),
                                ],
                                inheritPadding=True,
                                py="md",
                            ),
                        ],
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
                    dmc.Text(
                        "Sliders filter which titles qualify and how many bars render; hover and "
                        "scroll-zoom stay on the Plotly side.",
                        size="sm",
                        c="dimmed",
                        mb="xs",
                    ),
                    dmc.SimpleGrid(
                        cols={"base": 1, "sm": 2},
                        spacing="md",
                        children=[
                            dmc.Stack(
                                [
                                    dmc.Text("How many titles to show", size="sm", fw=600),
                                    dmc.Slider(
                                        id="q3-top-n",
                                        min=10,
                                        max=50,
                                        step=5,
                                        value=45,
                                        marks=_slider_marks(10, 50, 10),
                                    ),
                                ],
                                gap=6,
                            ),
                            dmc.Stack(
                                [
                                    dmc.Text("Minimum rows per title (noise filter)", size="sm", fw=600),
                                    dmc.Slider(
                                        id="q3-min-rows",
                                        min=1,
                                        max=20,
                                        step=1,
                                        value=1,
                                        marks=_slider_marks(1, 20, 5),
                                    ),
                                ],
                                gap=6,
                            ),
                        ],
                    ),
                    dmc.Text(id="q3-summary", size="sm", c="dimmed", mt="xs"),
                    dcc.Graph(
                        id="fig-authorities",
                        figure=fig_q3_top_authorities(df, top_n=45, min_opinion_rows=1),
                        style={"height": "720px"},
                        config=_GRAPH_CONFIG,
                    ),
                ],
                withBorder=True,
                shadow="sm",
            ),
        ],
        gap="md",
    )

    stats = df_stats_block(df)

    return dmc.MantineProvider(
        dmc.Container(
            [intro, stats, grid],
            fluid=True,
            p="md",
        )
    )


def df_stats_block(df: pd.DataFrame) -> dmc.Card:
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


def register_callbacks(app: Dash, df: pd.DataFrame) -> None:
    """Wire Mantine inputs to Plotly figures for charts 2 and 3."""

    @callback(
        Output("fig-q2-3d", "figure"),
        Output("q2-summary", "children"),
        Output("q2-filter-badges", "children"),
        Input("q2-court", "value"),
        Input("q2-rank-mode", "value"),
        Input("q2-top-n", "value"),
    )
    def update_q2(
        court: str | None, rank_mode: str | None, top_n: float | int | None
    ) -> tuple[go.Figure, str, list]:
        court_id = court or "wawd"
        mode = rank_mode if rank_mode in ("mean", "max") else "max"
        n = int(top_n) if top_n is not None else 45
        fig = fig_q2_scatter3d_jurisdiction(df, court_id=court_id, top_n=n, rank_mode=mode)
        rows_slice = int((df["court_id"] == court_id).sum())
        summary = (
            f"Mantine → pandas → Plotly 3D: court_id={court_id}, rank={mode}, top_n={n}. "
            f"Slice has {rows_slice:,} rows; full CSV has {len(df):,} rows."
        )
        badges = [
            dmc.Badge(f"court={court_id}", variant="light", color="violet"),
            dmc.Badge(f"rank={mode}", variant="light", color="gray"),
            dmc.Badge(f"top_n={n}", variant="outline", color="violet"),
        ]
        return fig, summary, badges

    @callback(
        Output("fig-authorities", "figure"),
        Output("q3-summary", "children"),
        Input("q3-top-n", "value"),
        Input("q3-min-rows", "value"),
    )
    def update_q3(top_n: float | int | None, min_rows: float | int | None) -> tuple[go.Figure, str]:
        n = int(top_n) if top_n is not None else 45
        mrows = int(min_rows) if min_rows is not None else 1
        fig = fig_q3_top_authorities(df, top_n=n, min_opinion_rows=mrows)
        summary = (
            f"Mantine → pandas: top_n={n}, min_opinion_rows={mrows}. "
            f"Titles must have at least {mrows} CSV row(s) before they can appear. "
            f"Full CSV has {len(df):,} rows."
        )
        return fig, summary


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
    fig2 = fig_q2_scatter3d_jurisdiction(df, court_id="wawd", top_n=45, rank_mode="max")
    fig3 = fig_q3_top_authorities(df, top_n=45, min_opinion_rows=1)

    if args.export:
        export_jpgs(fig1, fig2, fig3)
        return

    app = Dash(__name__)
    app.layout = build_layout(df, fig1)
    register_callbacks(app, df)
    # Local dev server — bind 127.0.0.1
    app.run(debug=False, host="127.0.0.1", port=8050)


if __name__ == "__main__":
    main()
