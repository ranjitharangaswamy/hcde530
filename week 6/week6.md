# Week 6: Plotly practice and mini trial questions

Week 6 is **not** the Mini Project submission. Here I practiced Plotly and Dash, and answered **small trial questions** with pandas on the same CourtListener CSV from Week 5.
Disclaimer: Used Cursor agent (AI) for language refinement and editing this week's markdown file.

The **three Mini Project questions** (judges and citations by court level, most cited cases in a jurisdiction, average cites and top authority titles) are only in **`MiniProject1/`**. They are **not** repeated below.

---

## What I did this week

1. Worked through `Week6_files/plotly-exercises.ipynb` (Plotly chart types, including when 3D is misleading).

2. Ran **`Week6_files/week6_mini_analytics.ipynb`**: short pandas counts and filters on the stacked export.

3. Kept **`courtlistener_mp1a_dash.py`** and **`mp1a_interactive_figures.ipynb`** as **Mini Project tooling** (three Plotly views for MP1). Week 6 grading for questions uses the mini notebook, not those charts.

4. Built **three interactive 2D charts** for the mini trial questions (`week6_charts.py` + last cells in `week6_mini_analytics.ipynb`), exported as PNG and HTML in `Week6_files/`. Revised from an earlier 3D draft after feedback that 3D did not fit this sparse, low-dimensional data.

5. Used a local venv (`week 6/.venv`) for Plotly, Kaleido, and Dash (same PEP 668 pattern as Week 5).

---

## Committed charts (mini trial questions)

| File | Trial question | Chart type | What it shows |
|------|----------------|------------|----------------|
| `Week6_files/week6_chart1_opinions_by_decision_year.png` | Q1 — rows decided in 2025? | **Grouped bar** (year × court) | Only **three** year×court cells in this export: **36,000** rows in **2025** on `washctapp`; federal `wawd` rows sit in **2018** (152) and **2019** (2,888), not 2025 |
| `Week6_files/week6_chart2_2025_criminal_vs_other_captions.png` | Q4 — criminal vs other in 2025? | **Horizontal bar** (2 categories) | Roughly one-third of 2025 captions match **State of Washington v.** criminal-style titles; remainder are other captions (title proxy only) |
| `Week6_files/week6_chart3_2025_family_title_keyword_rows.png` | Q2 — family-related titles in 2025? | **Horizontal bar** (2 categories) | Very few rows match family-law **keyword** titles; most 2025 rows do not — duplicate rows per caption inflate counts |

Matching `.html` files in the same folder are **fully interactive** (hover tooltips, scroll-zoom, pan). Open `Week6_files/week6_charts_interactive.html` for all three charts on one page, or any single `week6_chart*.html` file.

**Trial Q3 (federal `wawd` in 2025):** count is **0** in this export — a coverage finding, not plotted as its own chart. I note it in the notebook and below.

### Chart justifications (four-rule guide)

**Rule 1 — Match the data shape:** Chart 1 aggregates to year × court counts. After `groupby`, there are only three points (2018/wawd, 2019/wawd, 2025/washctapp). A 3D scatter treats z as a third spatial dimension; here count is the **value to compare**, so a grouped bar chart with labeled bars and comma-formatted counts is the correct encoding.

**Rule 2 — Avoid chart junk:** 3D rotation does not reveal structure that a 2D bar lacks when there is no continuous third variable. For charts 2 and 3, each question is a **two-category count**; horizontal bars let the reader compare criminal vs other (or family keyword vs no match) without pseudo-depth.

**Rule 3 — Say what the reader should take away:** Chart 1: coverage is dominated by 2025 state appellate rows. Chart 2: criminal-style titles are a minority but non-trivial share of 2025 captions. Chart 3: family keywords rarely appear in titles — a null-adjacent finding that should not be read as “no family cases in Washington.”

**Rule 4 — Honest limits on the data:** All three charts use **title text proxies** on opinion rows, not court docket codes. Chart 1’s subtitle notes sparse year×court cells; chart 3’s footnote states the keyword proxy limit.

### Competency claims (C6 visualization)

- **C6:** I matched chart type to dimensionality: grouped bars for year × court (three cells), horizontal bars for two-way 2025 splits. I labeled axes with units (decision year, opinion row counts, caption categories), put the headline finding in each title, added footnotes where the export is sparse or proxy-based, and exported static PNGs with Kaleido for the repo while keeping interactive HTML for exploration. I revised away from 3D after recognizing that Chart 1 had too few points and charts 2–3 had no meaningful third axis.

---

## Mini trial questions (Week 6 only)

Plain questions a stakeholder might ask. Each maps to one count or a small table in the notebook. **Not** the MP1 citation/judge threads.

| # | Trial question | What the notebook does |
|---|----------------|------------------------|
| 1 | How many **opinion rows** in this Seattle-area pull were **decided in 2025**? | Filter `date_of_decision` to year 2025; break out by `court_id` |
| 2 | In **2025**, how many rows have a **case title** that looks **family-related** (guardianship, dissolution, domestic, parentage, and similar words)? | Text filter on `case`; report row count and **unique** titles |
| 3 | How many **federal** Western District of Washington (`wawd`) opinions in **2025** are in this file? | Filter 2025 + `court_id == wawd` |
| 4 | In **2025**, how many rows look like **criminal appeals** (`State of Washington v. ...`) vs **other** captions? | Pattern on `case` title |

**Data honesty:** This file is CourtListener **opinions**, not a full civil docket with a "family law" code field. Question 2 is a **title keyword proxy**, not a court's case-type label. In this pull, **2025 rows are almost all** state appellate (`washctapp`, King County search). Federal Seattle rows (`wawd`) sit in **2018–2019**, so question 3 is **0** here. That is a coverage finding, not a broken filter.

---

## Connection to Mini Project 1

| Topic | Week 6 | MiniProject1 |
|-------|--------|----------------|
| Questions | Four mini trial counts (table above) | Three MP1 analytical questions in `Miniproject1.ipynb` |
| Charts | Three 2D trial-question PNGs/HTML in `Week6_files/` | Three JPGs + notebook Plotly |
| Data | `Week6_files/courtlistener_week5_repull_40k.csv` | `data/courtlistener.csv` (same stack) |

---

## Competencies (brief)

**C5 (pandas):** `read_csv`, year filter, `str.contains` on titles, `value_counts`, and grouping by `court_id` — e.g. the three-cell `groupby(["year", "court_id"])` table that feeds chart 1.

**C6 (visualization):** Plotly grouped and horizontal bar charts for trial questions; Kaleido PNG export; chart-type revision from 3D to 2D when point count and category count did not justify depth; justifications tied to the four-rule guide above.

**C7 (judgment):** I say when a trial question **cannot** be answered literally (no federal 2025 rows; "family law" inferred from titles only) and when a chart would mislead (3D on three aggregates or two bars).

---

## Files

| Path | Role |
|------|------|
| `Week6_files/week6_mini_analytics.ipynb` | **Week 6 trial questions** + 2D charts + export |
| `week6_charts.py` | Build/export trial-question figures |
| `Week6_files/week6_chart*.png` / `.html` | Committed static + interactive charts |
| `Week6_files/plotly-exercises.ipynb` | Course Plotly lab |
| `Week6_files/courtlistener_week5_repull_40k.csv` | Stacked export |
| `courtlistener_mp1a_dash.py` | MP1 only (not Week 6 questions) |
| `mp1a_interactive_figures.ipynb` | MP1 figures in Jupyter |
| `../MiniProject1/` | Submit MP1 here |
