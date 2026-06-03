"""
Week 6 — interactive 2D Plotly charts for mini trial questions.
Exports PNG (kaleido) and HTML to Week6_files/ (run from repo root or week 6/).

  python week6_charts.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

WEEK6_DIR = Path(__file__).resolve().parent
WEEK6_FILES = WEEK6_DIR / "Week6_files"
CSV_PATH = WEEK6_FILES / "courtlistener_week5_repull_40k.csv"
OUT_DIR = WEEK6_FILES

FAMILY_TITLE_PATTERN = (
    r"guardianship|dissolution|marital|parentage|paternity|domestic|"
    r"marriage|spousal|custody|divorce"
)
CRIMINAL_TITLE_PATTERN = r"State [Oo]f Washington,\s*V\.|State of Washington v\."

COURT_LABELS = {
    "washctapp": "State appellate (washctapp)",
    "wawd": "Federal W.D. Wash. (wawd)",
}

CHART_HEIGHT = 480
MARGIN = dict(t=88, l=48, r=24, b=72)

INTERACTIVE_CONFIG = {
    "scrollZoom": True,
    "displayModeBar": True,
    "displaylogo": False,
    "responsive": True,
}


def _apply_interactive(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        hovermode="closest",
        template="plotly_white",
    )
    fig.update_traces(hoverlabel=dict(namelength=-1))
    return fig


def load_df() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df["date_of_decision"] = pd.to_datetime(df["date_of_decision"], errors="coerce")
    return df


def chart1_opinions_by_year_court(df: pd.DataFrame) -> go.Figure:
    """Trial Q1: opinion rows by decision year and court (grouped bar)."""
    tmp = df.dropna(subset=["date_of_decision"]).copy()
    tmp["year"] = tmp["date_of_decision"].dt.year.astype(int)
    g = (
        tmp.groupby(["year", "court_id"], as_index=False)
        .size()
        .rename(columns={"size": "opinion_rows"})
        .sort_values(["year", "court_id"])
    )
    g["court_label"] = g["court_id"].map(COURT_LABELS).fillna(g["court_id"])
    g["year_court"] = g["year"].astype(str) + " — " + g["court_label"]

    n_2025 = int((tmp["year"] == 2025).sum())
    n_groups = len(g)

    fig = px.bar(
        g,
        x="year",
        y="opinion_rows",
        color="court_label",
        barmode="group",
        text="opinion_rows",
        hover_data={"court_id": True, "year_court": True},
        labels={
            "year": "Decision year",
            "opinion_rows": "Opinion rows",
            "court_label": "Court",
        },
        title=(
            f"Opinion rows by decision year and court "
            f"({n_2025:,} rows in 2025 of {len(df):,} total; {n_groups} year×court cells)"
        ),
        color_discrete_map={
            COURT_LABELS["washctapp"]: "#4C78A8",
            COURT_LABELS["wawd"]: "#F58518",
        },
    )
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(
        height=CHART_HEIGHT,
        margin=MARGIN,
        legend_title_text="Court",
        yaxis_tickformat=",",
        bargap=0.25,
    )
    fig.add_annotation(
        text=(
            "Sparse export: only three year×court combinations appear. "
            "2025 is almost entirely state appellate; federal wawd rows are 2018–2019."
        ),
        xref="paper",
        yref="paper",
        x=0,
        y=-0.22,
        showarrow=False,
        align="left",
        font=dict(size=11, color="#555"),
    )
    fig.update_layout(margin=dict(t=88, l=48, r=24, b=110))
    return _apply_interactive(fig)


def chart2_2025_criminal_vs_other(df: pd.DataFrame) -> go.Figure:
    """Trial Q4: criminal-style vs other captions in 2025 (vertical px.bar)."""
    df_2025 = df[df["date_of_decision"].dt.year == 2025]
    criminal = df_2025["case"].astype(str).str.contains(
        CRIMINAL_TITLE_PATTERN, case=False, na=False, regex=True
    )
    labels = [
        "Criminal-style title (State of Washington v. …)",
        "Other captions",
    ]
    counts = [int(criminal.sum()), int((~criminal).sum())]
    share = 100 * counts[0] / len(df_2025) if len(df_2025) else 0.0

    plot_df = pd.DataFrame(
        {"caption_type": labels, "opinion_rows": counts}
    )
    fig = px.bar(
        plot_df,
        x="caption_type",
        y="opinion_rows",
        color="caption_type",
        text="opinion_rows",
        labels={
            "caption_type": "Caption type",
            "opinion_rows": "Number of opinion rows",
        },
        title=(
            f"2025 caption split — criminal-style vs other (title proxy; "
            f"{share:.1f}% criminal-style of {len(df_2025):,} rows)"
        ),
        color_discrete_map={
            labels[0]: "#E45756",
            labels[1]: "#72B7B2",
        },
    )
    fig.update_traces(
        texttemplate="%{text:,}",
        textposition="outside",
        hovertemplate="%{x}<br>%{y:,} opinion rows<extra></extra>",
    )
    fig.update_layout(
        height=CHART_HEIGHT,
        margin=MARGIN,
        showlegend=False,
        xaxis_title="",
        yaxis_tickformat=",",
    )
    return _apply_interactive(fig)


def chart3_2025_family_keyword(df: pd.DataFrame) -> go.Figure:
    """Trial Q2: family-related title keywords in 2025 (horizontal bar)."""
    df_2025 = df[df["date_of_decision"].dt.year == 2025]
    family = df_2025["case"].astype(str).str.contains(
        FAMILY_TITLE_PATTERN, case=False, na=False, regex=True
    )
    n_family = int(family.sum())
    n_other = len(df_2025) - n_family
    n_unique = int(df_2025.loc[family, "case"].nunique())

    labels = ["Family-related keywords", "No keyword match"]
    counts = [n_family, n_other]

    fig = go.Figure(
        data=[
            go.Bar(
                y=labels,
                x=counts,
                orientation="h",
                marker_color=["#F58518", "#BAB0AC"],
                text=[f"{n:,}" for n in counts],
                textposition="outside",
                hovertemplate="%{y}<br>%{x:,} rows<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=(
            f"2025 family-law title keyword proxy — {n_family:,} rows "
            f"({n_unique} unique title{'s' if n_unique != 1 else ''} of {len(df_2025):,})"
        ),
        height=CHART_HEIGHT,
        margin=MARGIN,
        template="plotly_white",
        xaxis_title="Number of opinion rows",
        yaxis_title="",
        xaxis_tickformat=",",
    )
    fig.add_annotation(
        text="Title keyword proxy only — not a court case-type field.",
        xref="paper",
        yref="paper",
        x=0,
        y=-0.18,
        showarrow=False,
        align="left",
        font=dict(size=11, color="#555"),
    )
    fig.update_layout(margin=dict(t=88, l=48, r=24, b=96))
    return _apply_interactive(fig)


def build_all_figures(df: pd.DataFrame | None = None) -> list[tuple[str, go.Figure]]:
    data = load_df() if df is None else df
    return [
        ("Chart 1 — year × court (trial Q1)", chart1_opinions_by_year_court(data)),
        ("Chart 2 — criminal vs other 2025 (trial Q4)", chart2_2025_criminal_vs_other(data)),
        ("Chart 3 — family keywords 2025 (trial Q2)", chart3_2025_family_keyword(data)),
    ]


def combined_interactive_html(df: pd.DataFrame | None = None) -> go.Figure:
    """Single-page HTML with three stacked interactive figures."""
    from plotly.subplots import make_subplots

    data = load_df() if df is None else df
    c1 = chart1_opinions_by_year_court(data)
    c2 = chart2_2025_criminal_vs_other(data)
    c3 = chart3_2025_family_keyword(data)
    fig = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=(
            "Q1 — Opinion rows by year and court",
            "Q4 — 2025 criminal-style vs other captions",
            "Q2 — 2025 family title keyword proxy",
        ),
        vertical_spacing=0.1,
        specs=[[{"type": "xy"}], [{"type": "xy"}], [{"type": "xy"}]],
    )
    for trace in c1.data:
        fig.add_trace(trace, row=1, col=1)
    for trace in c2.data:
        fig.add_trace(trace, row=2, col=1)
    for trace in c3.data:
        fig.add_trace(trace, row=3, col=1)
    fig.update_layout(
        height=1400,
        showlegend=True,
        title_text="Week 6 trial questions — interactive 2D charts (hover, zoom, pan)",
        hovermode="closest",
    )
    fig.update_xaxes(title_text="Decision year", row=1, col=1)
    fig.update_yaxes(title_text="Opinion rows", row=1, col=1, tickformat=",")
    fig.update_yaxes(title_text="Opinion rows", tickformat=",", row=2, col=1)
    fig.update_yaxes(title_text="Opinion rows", tickformat=",", row=3, col=1)
    return _apply_interactive(fig)


# Backward-compatible aliases (notebook may still reference old names)
chart1_opinions_by_year_court_3d = chart1_opinions_by_year_court
chart2_2025_criminal_vs_other_3d = chart2_2025_criminal_vs_other
chart3_2025_family_keyword_3d = chart3_2025_family_keyword


def export_all(*, show: bool = False) -> list[Path]:
    df = load_df()
    charts = [
        ("week6_chart1_opinions_by_decision_year", chart1_opinions_by_year_court(df)),
        ("week6_chart2_2025_criminal_vs_other_captions", chart2_2025_criminal_vs_other(df)),
        ("week6_chart3_2025_family_title_keyword_rows", chart3_2025_family_keyword(df)),
    ]
    written: list[Path] = []
    for stem, fig in charts:
        png = OUT_DIR / f"{stem}.png"
        html = OUT_DIR / f"{stem}.html"
        fig.write_image(str(png), format="png", scale=2, width=1100, height=fig.layout.height)
        fig.write_html(
            str(html),
            include_plotlyjs="cdn",
            config=INTERACTIVE_CONFIG,
        )
        written.extend([png, html])
        print(f"Wrote {png}")
        print(f"Wrote {html} (interactive — open in a browser)")
        if show:
            fig.show(config=INTERACTIVE_CONFIG)
    combo = OUT_DIR / "week6_charts_interactive.html"
    combined_interactive_html(df).write_html(
        str(combo),
        include_plotlyjs="cdn",
        config=INTERACTIVE_CONFIG,
    )
    written.append(combo)
    print(f"Wrote {combo} (all three charts on one page)")
    return written


if __name__ == "__main__":
    export_all()
