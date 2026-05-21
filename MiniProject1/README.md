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
| `images/mp1a_chart*.jpg` | Static chart exports (Kaleido) |
| `mp1_charts.py` | Plotly figure builders + export helper |

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

Optional interactive Dash app (same three questions) lives in the course repo at `week 6/courtlistener_mp1a_dash.py` and writes JPGs into `images/`.
