# Mini Project 1 — CourtListener Citation Analysis

Standalone portfolio folder for HCDE 530. Everything needed to review or re-run the **full** analysis is here.

**Week 6** in the repo covers Plotly practice and **mini** pandas questions (row counts, year filters). This folder holds the **three main analytical questions** and the charts that answer them.

## Three analytical questions (MP1a)

1. Which judges author the most cited opinions — and does citation frequency vary by **court level**?
2. What are the **most cited judgments** in a specific jurisdiction? (Western District of Washington in this dataset.)
3. What is the **average** cite behavior per opinion row, and which **case titles** accumulate the most citation mass?

See **Section 1** in `Miniproject1.ipynb` for narrative, caveats (state `cite_count` all zero in this pull), and interpretations.

## Contents

| Path | Purpose |
|------|---------|
| `Miniproject1.ipynb` | Main narrative notebook (run top to bottom) |
| `data/courtlistener.csv` | Source data (~39k CourtListener opinion rows) |
| `images/mp1a_chart*.jpg` | Static chart exports (Kaleido; matches notebook figures) |
| `mp1_charts.py` | Plotly figure builders + export helper |
| `mp1_dash.py` | Interactive [Dash gallery](https://dash.gallery/Portal/)-style app (Mantine + Plotly) |
| `mp1.md` | Glossary, Section 4 conclusions (per question), Section 5 process, competency claims |

## Run the notebook

1. Open `Miniproject1.ipynb` in Jupyter or VS Code.
2. Set the kernel working directory to **this folder** (`MiniProject1/`).
3. **Kernel → Restart & Run All** (first cell installs `jupyter`, `plotly`, `kaleido`, `pandas`).

## Regenerate chart images only

```bash
cd MiniProject1
python3 mp1_charts.py
```

Requires `pandas`, `plotly`, and `kaleido`.

## Interactive dashboard (recommended for exploration)

```bash
cd MiniProject1
pip install -r requirements.txt
python mp1_dash.py
```

Open **http://127.0.0.1:8050/** — rotate 3D charts, use sliders for court / rank / top-N, and box-select bars on chart (c).

Export JPGs from the same figures:

```bash
python mp1_dash.py --export
```
