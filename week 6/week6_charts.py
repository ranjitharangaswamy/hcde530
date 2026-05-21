"""
Week 6 — interactive 3D Plotly charts for mini trial questions.
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

# Mesh3d box faces (Plotly week-6 lab pattern)
_BOX_I = [7, 0, 0, 0, 4, 4, 6, 1, 4, 0, 3, 6]
_BOX_J = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 7]
_BOX_K = [0, 7, 2, 3, 6, 7, 1, 6, 5, 5, 7, 2]

SCENE_BG = "rgb(248,249,252)"


def load_df() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df["date_of_decision"] = pd.to_datetime(df["date_of_decision"], errors="coerce")
    return df


def _mesh_bar(
    x_center: float,
    y_center: float,
    height: float,
    *,
    width: float = 0.65,
    color: str = "#4C78A8",
    hover: str = "",
) -> go.Mesh3d:
    half = width / 2
    xs = [x_center - half, x_center + half, x_center + half, x_center - half] * 2
    ys = [y_center - half, y_center - half, y_center + half, y_center + half] * 2
    zs = [0, 0, 0, 0, height, height, height, height]
    return go.Mesh3d(
        x=xs,
        y=ys,
        z=zs,
        i=_BOX_I,
        j=_BOX_J,
        k=_BOX_K,
        color=color,
        opacity=0.92,
        flatshading=True,
        hovertext=hover,
        hoverinfo="text",
        showscale=False,
    )


def _scene_defaults() -> dict:
    axis = dict(backgroundcolor=SCENE_BG, gridcolor="white", showbackground=True)
    return dict(
        bgcolor=SCENE_BG,
        xaxis={**axis},
        yaxis={**axis},
        zaxis={**axis},
        camera=dict(eye=dict(x=1.45, y=1.35, z=0.95)),
    )


def chart1_opinions_by_year_court_3d(df: pd.DataFrame) -> go.Figure:
    """Trial Q1: opinion rows by decision year and court (3D scatter)."""
    tmp = df.dropna(subset=["date_of_decision"]).copy()
    tmp["year"] = tmp["date_of_decision"].dt.year.astype(int)
    g = (
        tmp.groupby(["year", "court_id"], as_index=False)
        .size()
        .rename(columns={"size": "opinion_rows"})
        .sort_values(["year", "court_id"])
    )
    g["court_label"] = g["court_id"].map(COURT_LABELS).fillna(g["court_id"])
    g["court_code"] = g["court_id"].map({"washctapp": 0.0, "wawd": 1.0}).fillna(0.5)

    n_2025 = int((tmp["year"] == 2025).sum())
    fig = px.scatter_3d(
        g,
        x="year",
        y="court_code",
        z="opinion_rows",
        color="court_label",
        size="opinion_rows",
        size_max=42,
        hover_data={
            "court_id": True,
            "opinion_rows": True,
            "court_code": False,
        },
        title=(
            "Opinion rows by decision year and court — 3D view "
            f"({n_2025:,} rows decided in 2025 of {len(df):,} total)"
        ),
    )
    fig.update_layout(
        height=560,
        margin=dict(t=72, l=0, r=0, b=0),
        legend_title_text="Court",
        scene=_scene_defaults()
        | dict(
            xaxis_title="Decision year",
            yaxis_title="Court (0 = washctapp, 1 = wawd)",
            zaxis_title="Number of opinion rows",
        ),
    )
    return fig


def chart2_2025_criminal_vs_other_3d(df: pd.DataFrame) -> go.Figure:
    """Trial Q4: criminal-style vs other captions in 2025 (3D bar towers)."""
    df_2025 = df[df["date_of_decision"].dt.year == 2025]
    criminal = df_2025["case"].astype(str).str.contains(
        CRIMINAL_TITLE_PATTERN, case=False, na=False, regex=True
    )
    counts = {
        "Criminal-style title\n(State of Washington v. …)": int(criminal.sum()),
        "Other captions": int((~criminal).sum()),
    }
    colors = ["#E45756", "#72B7B2"]
    bars = []
    for i, (label, n) in enumerate(counts.items()):
        bars.append(
            _mesh_bar(
                float(i),
                0.0,
                float(max(n, 1)),
                color=colors[i],
                hover=f"{label.replace(chr(10), ' ')}<br>{n:,} opinion rows",
            )
        )
    share = 100 * counts["Criminal-style title\n(State of Washington v. …)"] / len(df_2025)
    fig = go.Figure(data=bars)
    fig.update_layout(
        title=(
            f"2025 caption split — criminal-style vs other (title proxy; "
            f"{share:.1f}% criminal-style of {len(df_2025):,} rows)"
        ),
        height=520,
        margin=dict(t=80),
        template="plotly_white",
        scene=_scene_defaults()
        | dict(
            xaxis=dict(
                title="Caption type (2025)",
                tickmode="array",
                tickvals=[0, 1],
                ticktext=["Criminal-style", "Other"],
            ),
            yaxis=dict(title="", showticklabels=False, range=[-1, 1]),
            zaxis_title="Number of opinion rows",
        ),
    )
    return fig


def chart3_2025_family_keyword_3d(df: pd.DataFrame) -> go.Figure:
    """Trial Q2: family-related title keywords in 2025 (3D bar towers)."""
    df_2025 = df[df["date_of_decision"].dt.year == 2025]
    family = df_2025["case"].astype(str).str.contains(
        FAMILY_TITLE_PATTERN, case=False, na=False, regex=True
    )
    n_family = int(family.sum())
    n_other = len(df_2025) - n_family
    n_unique = int(df_2025.loc[family, "case"].nunique())
    counts = {
        "Family-related\nkeywords": n_family,
        "No keyword\nmatch": n_other,
    }
    colors = ["#F58518", "#BAB0AC"]
    bars = []
    for i, (label, n) in enumerate(counts.items()):
        bars.append(
            _mesh_bar(
                float(i),
                0.0,
                float(max(n, 1)),
                color=colors[i],
                hover=f"{label.replace(chr(10), ' ')}<br>{n:,} rows",
            )
        )
    fig = go.Figure(data=bars)
    fig.update_layout(
        title=(
            f"2025 family-law title keyword proxy — {n_family:,} rows "
            f"({n_unique} unique title{'s' if n_unique != 1 else ''} of {len(df_2025):,})"
        ),
        height=520,
        margin=dict(t=80),
        template="plotly_white",
        scene=_scene_defaults()
        | dict(
            xaxis=dict(
                title="Title keyword proxy (2025)",
                tickmode="array",
                tickvals=[0, 1],
                ticktext=["Family keywords", "No match"],
            ),
            yaxis=dict(title="", showticklabels=False, range=[-1, 1]),
            zaxis_title="Number of opinion rows",
        ),
    )
    return fig


def export_all(*, show: bool = False) -> list[Path]:
    df = load_df()
    charts = [
        ("week6_chart1_opinions_by_decision_year", chart1_opinions_by_year_court_3d(df)),
        ("week6_chart2_2025_criminal_vs_other_captions", chart2_2025_criminal_vs_other_3d(df)),
        ("week6_chart3_2025_family_title_keyword_rows", chart3_2025_family_keyword_3d(df)),
    ]
    written: list[Path] = []
    for stem, fig in charts:
        png = OUT_DIR / f"{stem}.png"
        html = OUT_DIR / f"{stem}.html"
        fig.write_image(str(png), format="png", scale=2, width=1100, height=fig.layout.height)
        fig.write_html(str(html), include_plotlyjs="cdn")
        written.extend([png, html])
        print(f"Wrote {png}")
        print(f"Wrote {html}")
        if show:
            fig.show()
    return written


if __name__ == "__main__":
    export_all()
