"""
HCDE 530 — Mini Project 1 interactive dashboard (Plotly Dash + Mantine).

Gallery-style UI with sliders, filters, and linked Plotly charts — see:
https://dash.gallery/Portal/

Data: MiniProject1/data/courtlistener.csv

Run:
  cd MiniProject1
  python mp1_dash.py

Export static JPGs (same figures as the notebook):
  python mp1_dash.py --export
"""

from __future__ import annotations

import argparse
from types import SimpleNamespace

import mp1_charts as charts
import plotly.graph_objects as go

_dash_ui: SimpleNamespace | None = None


def _dash_mantine_stack() -> SimpleNamespace:
    global _dash_ui
    if _dash_ui is None:
        import dash_mantine_components as dmc
        from dash import Dash, Input, Output, callback, dcc

        _dash_ui = SimpleNamespace(
            dmc=dmc,
            Dash=Dash,
            Input=Input,
            Output=Output,
            callback=callback,
            dcc=dcc,
        )
    return _dash_ui


def _court_select_data() -> list[dict[str, str]]:
    return [
        {"value": "wawd", "label": "Federal — W.D. Wash. (wawd)"},
        {"value": "washctapp", "label": "State — Wash. Ct. App. / King County pull (washctapp)"},
    ]


def _slider_marks(min_v: int, max_v: int, step: int) -> list[dict]:
    return [{"value": v, "label": str(v)} for v in range(min_v, max_v + 1, step)]


def _q2_default_badges() -> list:
    dmc = _dash_mantine_stack().dmc
    return [
        dmc.Badge("court=wawd", variant="light", color="violet"),
        dmc.Badge("rank=max", variant="light", color="gray"),
        dmc.Badge(f"top_n=45", variant="outline", color="violet"),
    ]


def kpi_cards(df) -> object:
    dmc = _dash_mantine_stack().dmc
    n = len(df)
    n_wawd = int((df["court_id"] == "wawd").sum())
    n_wash = int((df["court_id"] == "washctapp").sum())
    mean_all = float(df["cite_count"].mean())
    mean_wawd = float(df.loc[df["court_id"] == "wawd", "cite_count"].mean())

    def stat_card(label: str, value: str, hint: str) -> object:
        return dmc.Card(
            dmc.Stack(
                [
                    dmc.Text(label, size="xs", tt="uppercase", fw=700, c="dimmed"),
                    dmc.Text(value, size="xl", fw=700),
                    dmc.Text(hint, size="xs", c="dimmed"),
                ],
                gap=4,
            ),
            withBorder=True,
            padding="md",
            radius="md",
        )

    return dmc.SimpleGrid(
        cols={"base": 1, "sm": 2, "lg": 4},
        spacing="md",
        children=[
            stat_card("Opinion rows", f"{n:,}", "Full CourtListener extract"),
            stat_card("Federal (wawd)", f"{n_wawd:,}", f"Mean cite {mean_wawd:.2f}"),
            stat_card("State (washctapp)", f"{n_wash:,}", "cite_count = 0 in this pull"),
            stat_card("Overall mean cite", f"{mean_all:.4f}", "Dominated by zero-heavy state rows"),
        ],
    )


def df_stats_block(df) -> object:
    dmc = _dash_mantine_stack().dmc
    mean_all = float(df["cite_count"].mean())
    mean_wawd = float(df.loc[df["court_id"] == "wawd", "cite_count"].mean())
    mean_wash = float(df.loc[df["court_id"] == "washctapp", "cite_count"].mean())
    j = charts.agg_judge_federal(df, top_n=5)
    judge_lines = [
        f"{row.judge_clean}: mean cite {row.mean_cite_count:.2f} ({int(row.opinion_count)} opinions)"
        for row in j.itertuples()
    ]
    judge_text = (
        "Top federal judges by mean cite_count: " + " · ".join(judge_lines)
        if len(j)
        else "No judge strings available to rank."
    )
    return dmc.Card(
        [
            dmc.Title("Judge / court narrative (tabular)", order=4),
            dmc.Text(
                "State rows omit judges and cite_count is uniformly 0 here — compare courts "
                "before inferring how 'cited' local opinions are.",
                size="sm",
            ),
            dmc.Text(judge_text, size="sm"),
            dmc.Divider(my="sm"),
            dmc.Text(
                f"Mean cite_count — all rows: {mean_all:.4f}; wawd: {mean_wawd:.4f}; "
                f"washctapp: {mean_wash:.4f}.",
                size="sm",
            ),
        ],
        withBorder=True,
        shadow="xs",
        p="md",
        mb="md",
    )


def build_layout(df, fig1: go.Figure) -> object:
    ui = _dash_mantine_stack()
    dmc, dcc = ui.dmc, ui.dcc

    intro = dmc.Stack(
        [
            dmc.Group(
                [
                    dmc.Title("Mini Project 1 — CourtListener citations", order=2),
                    dmc.Badge("Dash + Mantine", variant="light", color="violet"),
                    dmc.Anchor(
                        "Dash gallery",
                        href="https://dash.gallery/Portal/",
                        target="_blank",
                        size="sm",
                    ),
                ],
                gap="sm",
                align="flex-end",
            ),
            dmc.Text(
                f"Interactive views on `data/courtlistener.csv` ({len(df):,} rows). "
                "Line and treemap views for (a) and (c); rotate chart (b) in 3D. Mantine sliders refilter (b) and (c).",
                size="sm",
                c="dimmed",
            ),
            dmc.Alert(
                "Finding: cite_count is 0 for every Wash. Ct. App. row in this extract; "
                "non-zero cites appear only in the W.D. Wash. slice.",
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
                                dmc.Title("Question (a) — court level & time (line chart)", order=4),
                                inheritPadding=True,
                                py="xs",
                            ),
                            dcc.Graph(
                                id="fig-3d",
                                figure=fig1,
                                style={"height": "620px"},
                                config=charts.GRAPH_CONFIG,
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
                                                    ],
                                                    gap="xs",
                                                ),
                                                dmc.Text(
                                                    "Drag to orbit · scroll to zoom · sliders update the slice.",
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
                                    dmc.Paper(
                                        p="md",
                                        radius="sm",
                                        withBorder=True,
                                        bg="var(--mantine-color-gray-0)",
                                        children=[
                                            dmc.Group(
                                                [
                                                    dmc.Text(
                                                        "Active filters",
                                                        size="xs",
                                                        tt="uppercase",
                                                        fw=700,
                                                        c="dimmed",
                                                    ),
                                                    dmc.Group(
                                                        id="q2-filter-badges",
                                                        gap="xs",
                                                        children=_q2_default_badges(),
                                                    ),
                                                ],
                                                justify="space-between",
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
                                                            dmc.Select(
                                                                id="q2-court",
                                                                data=_court_select_data(),
                                                                value="wawd",
                                                                searchable=True,
                                                                clearable=False,
                                                                w="100%",
                                                            ),
                                                        ],
                                                        gap=6,
                                                    ),
                                                    dmc.Stack(
                                                        [
                                                            dmc.Text("Rank case titles by", size="sm", fw=600),
                                                            dmc.SegmentedControl(
                                                                id="q2-rank-mode",
                                                                data=[
                                                                    {"value": "max", "label": "Max cite / title"},
                                                                    {"value": "mean", "label": "Mean cite / title"},
                                                                ],
                                                                value="max",
                                                                fullWidth=True,
                                                                color="violet",
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
                                        figure=charts.fig_q2_scatter3d_jurisdiction(
                                            df, court_id="wawd", top_n=45, rank_mode="max"
                                        ),
                                        style={"height": "700px"},
                                        config=charts.GRAPH_CONFIG,
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
                        dmc.Title("Question (c) — citation mass by title (treemap)", order=4),
                        inheritPadding=True,
                        py="xs",
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
                                        color="violet",
                                    ),
                                ],
                                gap=6,
                            ),
                            dmc.Stack(
                                [
                                    dmc.Text("Minimum rows per title", size="sm", fw=600),
                                    dmc.Slider(
                                        id="q3-min-rows",
                                        min=1,
                                        max=20,
                                        step=1,
                                        value=1,
                                        marks=_slider_marks(1, 20, 5),
                                        color="violet",
                                    ),
                                ],
                                gap=6,
                            ),
                        ],
                    ),
                    dmc.Text(id="q3-summary", size="sm", c="dimmed", mt="xs"),
                    dcc.Graph(
                        id="fig-authorities",
                        figure=charts.fig_q3_top_authorities(df, top_n=45, min_opinion_rows=1),
                        style={"height": "720px"},
                        config=charts.GRAPH_CONFIG,
                    ),
                ],
                withBorder=True,
                shadow="sm",
            ),
        ],
        gap="md",
    )

    return dmc.MantineProvider(
        dmc.Container([intro, kpi_cards(df), df_stats_block(df), grid], fluid=True, p="md")
    )


def register_callbacks(app, df) -> None:
    ui = _dash_mantine_stack()
    dmc = ui.dmc
    callback = ui.callback
    Input = ui.Input
    Output = ui.Output

    @callback(
        Output("fig-q2-3d", "figure"),
        Output("q2-summary", "children"),
        Output("q2-filter-badges", "children"),
        Input("q2-court", "value"),
        Input("q2-rank-mode", "value"),
        Input("q2-top-n", "value"),
    )
    def update_q2(court, rank_mode, top_n):
        court_id = court or "wawd"
        mode = rank_mode if rank_mode in ("mean", "max") else "max"
        n = int(top_n) if top_n is not None else 45
        fig = charts.fig_q2_scatter3d_jurisdiction(df, court_id=court_id, top_n=n, rank_mode=mode)
        rows_slice = int((df["court_id"] == court_id).sum())
        summary = (
            f"Filters → Plotly 3D: court_id={court_id}, rank={mode}, top_n={n}. "
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
    def update_q3(top_n, min_rows):
        n = int(top_n) if top_n is not None else 45
        mrows = int(min_rows) if min_rows is not None else 1
        fig = charts.fig_q3_top_authorities(df, top_n=n, min_opinion_rows=mrows)
        summary = (
            f"Filters → horizontal bar chart: top_n={n}, min_opinion_rows={mrows}. "
            f"Box-select bars to highlight; full CSV has {len(df):,} rows."
        )
        return fig, summary


def create_app(df=None):
    ui = _dash_mantine_stack()
    if df is None:
        df = charts.load_df()
    fig1 = charts.fig_q1_scatter3d_monthly(df)
    app = ui.Dash(__name__)
    app.layout = build_layout(df, fig1)
    register_callbacks(app, df)
    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", action="store_true", help="Write JPGs to images/ and exit.")
    parser.add_argument("--port", type=int, default=8050)
    args = parser.parse_args()

    df = charts.load_df()
    fig1 = charts.fig_q1_scatter3d_monthly(df)
    fig2 = charts.fig_q2_scatter3d_jurisdiction(df, court_id="wawd", top_n=45, rank_mode="max")
    fig3 = charts.fig_q3_top_authorities(df, top_n=45, min_opinion_rows=1)

    if args.export:
        charts.export_chart_images(fig1, fig2, fig3)
        return

    app = create_app(df)
    print(f"Open http://127.0.0.1:{args.port}/ — Ctrl+C to stop.")
    app.run(debug=False, host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
