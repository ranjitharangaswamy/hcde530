# Week 6: Plotly practice and mini trial questions

Week 6 is **not** the Mini Project submission. Here I practiced Plotly and Dash, and answered **small trial questions** with pandas on the same CourtListener CSV from Week 5.
Disclaimer: Used Cursor agent (AI) for language refinement and editing this week's markdown file.

The **three Mini Project questions** (judges and citations by court level, most cited cases in a jurisdiction, average cites and top authority titles) are only in **`MiniProject1/`**. They are **not** repeated below.

---

## What I did this week

1. Worked through `Week6_files/plotly-exercises.ipynb` (3D scatter, chart type choices).

2. Ran **`Week6_files/week6_mini_analytics.ipynb`**: short pandas counts and filters on the stacked export.

3. Kept **`courtlistener_mp1a_dash.py`** and **`mp1a_interactive_figures.ipynb`** as **Mini Project tooling** (three Plotly views for MP1). Week 6 grading for questions uses the mini notebook, not those charts.

4. Built **three interactive 3D charts** for the mini trial questions (`week6_charts.py` + last cells in `week6_mini_analytics.ipynb`), exported as PNG and HTML in `Week6_files/`.

5. Used a local venv (`week 6/.venv`) for Plotly, Kaleido, and Dash (same PEP 668 pattern as Week 5).

---

## Committed charts (mini trial questions)

| File | Trial question | Chart type | What it shows |
|------|----------------|------------|----------------|
| `Week6_files/week6_chart1_opinions_by_decision_year.png` | Q1 — rows decided in 2025? | **3D scatter** (year × court × row count) | Most rows sit in **2025** on state appellate (`washctapp`); federal `wawd` appears in **2018–2019**, not 2025 |
| `Week6_files/week6_chart2_2025_criminal_vs_other_captions.png` | Q4 — criminal vs other in 2025? | **3D bar towers** (Mesh3d) | Roughly one-third of 2025 captions match **State of Washington v.** criminal-style titles; remainder are other captions (proxy only) |
| `Week6_files/week6_chart3_2025_family_title_keyword_rows.png` | Q2 — family-related titles in 2025? | **3D bar towers** (Mesh3d) | Very few rows match family-law **keyword** titles; most 2025 rows do not — and duplicate rows per caption inflate counts |

Matching `.html` files in the same folder preserve **rotate / zoom / hover** for grading review.

**Trial Q3 (federal `wawd` in 2025):** count is **0** in this export — a coverage finding, not plotted as its own chart. I note it in the notebook and below.

### Chart justifications (four-rule guide)

1. **Chart 1 — 3D scatter, not a flat bar chart:** Year and court are two independent dimensions; height (z) is row count. A 3D scene lets you see that 2025 stacks on `washctapp` while federal rows live in earlier years — a pattern easy to miss in a single 2D bar.

2. **Chart 2 — 3D towers for a binary split:** Only two categories, but Mesh3d bars match the course 3D bar pattern and make the **magnitude gap** between criminal-style and other captions readable from multiple angles.

3. **Chart 3 — 3D towers for keyword proxy:** Same rationale; the family bucket is small relative to “no match,” so a tall “other” tower is the main visual story (null-adjacent finding: keywords rarely fire).

### Competency claims (C6 visualization)

- **C6:** I chose chart types to match each question (time × court → 3D scatter; two-way splits → 3D bars), labeled axes with units (years, row counts, caption types), titled each chart with the finding, and exported static PNGs with Kaleido for repo submission while keeping interactive HTML for exploration.

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
| Charts | Three 3D trial-question PNGs/HTML in `Week6_files/` | Three JPGs + notebook Plotly |
| Data | `Week6_files/courtlistener_week5_repull_40k.csv` | `data/courtlistener.csv` (same stack) |

---

## Competencies (brief)

**C5 (pandas):** `read_csv`, year filter, `str.contains` on titles, `value_counts`, and grouping by `court_id`.

**C6 (visualization):** Plotly 3D scatter and Mesh3d bars for trial questions; Kaleido PNG export; chart justifications above.

**C7 (judgment):** I say when a trial question **cannot** be answered literally (no federal 2025 rows; "family law" inferred from titles only).

---

## Files

| Path | Role |
|------|------|
| `Week6_files/week6_mini_analytics.ipynb` | **Week 6 trial questions** + 3D charts + export |
| `week6_charts.py` | Build/export trial-question figures |
| `Week6_files/week6_chart*.png` / `.html` | Committed static + interactive charts |
| `Week6_files/plotly-exercises.ipynb` | Course Plotly lab |
| `Week6_files/courtlistener_week5_repull_40k.csv` | Stacked export |
| `courtlistener_mp1a_dash.py` | MP1 only (not Week 6 questions) |
| `mp1a_interactive_figures.ipynb` | MP1 figures in Jupyter |
| `../MiniProject1/` | Submit MP1 here |
