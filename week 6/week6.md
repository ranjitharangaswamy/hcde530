# Week 6 — MP1a CourtListener visualizations

## Competency claim

I can take a **large, messy administrative dataset** (39,040 opinion rows from CourtListener), **profile coverage limits** (missing judges, zero-heavy citation fields), **aggregate responsibly** to a **lightweight interactive surface** (~45–48 plotted points per heavy chart, with explicit counts in titles), and **pair the right chart type to each analytical question** while documenting **null or flat findings** as real results.

## Analytical questions (MP1a) and what each chart shows

### (a) Judges, citation frequency, and court level

**Question:** Which judges author opinions that are most frequently cited by other cases in the dataset, and does citation frequency vary by court level?

**Chart:** `mp1a_chart1_court_level_cites_3d.jpg` — 3D scatter of **monthly mean `cite_count`** by **court level** (encoded as `court_id`: Wash. Court of Appeals vs. W.D. Wash.), with **bubble size = opinion count** in that month/court bucket.

**Justification (chart type):** The MP1 guide’s “four-rule” logic favors **comparing distributions across categories and time** with a **relationship** view when three quantitative channels exist (time, court stratum, mean cites). A **3D scatter** makes the separation between strata visible while keeping the plot sparse enough to read; hover carries exact aggregates.

**Findings / limitations (honest nulls):**

- In this pull, **every** `washctapp` (King County, Wash. Ct. App.) row has `cite_count = 0` and **no judge field**, so **court-level contrast is extreme**: federal district opinions carry *all* non-zero citation signal in this file.
- Judge-level ranking is therefore **not shown as its own chart** (it would duplicate the federal-only slice and violate “one question per chart”). Instead, the Dash view includes a **Mantine text card** summarizing **top federal judges by mean `cite_count`** over ~2.9k opinions with judge strings.

### (b) Most cited judgments in a specific jurisdiction

**Question:** Which judgments are most cited within a chosen jurisdiction?

**Chart:** `mp1a_chart2_top_cited_cases_wd_wash.jpg` — horizontal **bar chart** of the **top 45 case titles** in **W.D. Wash.** (`court_id = wawd`), using **`max(cite_count)` per title** after collapsing duplicate rows.

**Justification:** For **ordered categorical labels** (long case names) and a **bounded magnitude** (`cite_count`), a **horizontal bar chart** maximizes readable label space and supports direct comparison.

**Findings:** The distribution is **heavily skewed** toward a small set of titles (notably *O’Connor v. Berryhill* appears many times at the maximum score in this pull). Wash. Ct. App. rows are **flat at zero** for this field, so that jurisdiction would not support a meaningful “most cited” bar chart in **this** extract.

### (c) Average citation clusters per opinion and “central” case titles

**Question:** What is the average number of citation clusters per opinion, and which case names appear most often as cited authorities across the dataset?

**Chart:** `mp1a_chart3_top_authority_titles.jpg` — horizontal **bar chart** of the **top 45 case titles** ranked by **`sum(cite_count)`** across all rows for that title, with color encoding **how many rows** each title has in the pull.

**Justification:** The question mixes a **global average** (scalar) with **heavy-tailed skew** across titles. A **bar chart of summed cites** surfaces which titles dominate total incoming citation mass, while the **title states the dataset-wide mean** for interpretability.

**Findings:**

- **Mean `cite_count` per opinion row** is **~0.152** clusters (because ~36k rows are identically zero in the state slice).
- “Cited authority” is **operationalized** here as **incoming `cite_count` mass** attributed to each case title in this snapshot (CourtListener’s field, not a separate extracted citation graph).

## Reproducibility — interactive Dash app

- **Script:** `courtlistener_mp1a_dash.py`
- **UI primitives:** [Dash Mantine Components](https://www.dash-mantine-components.com/getting-started) (`MantineProvider`, `Container`, `Stack`, `SimpleGrid`, `Card`, `Alert`, `Title`, `Text`, `Divider`).
- **Charts:** Plotly (`scatter_3d`, `bar`).
- **Run locally** (from repo root or `week 6/`):

```bash
"week 6/.venv/bin/python" "week 6/courtlistener_mp1a_dash.py"
```

Then open `http://127.0.0.1:8050` in a browser.

- **Export JPGs** (committed artifacts for the rubric):

```bash
"week 6/.venv/bin/python" "week 6/courtlistener_mp1a_dash.py" --export
```

> Note: the course rubric mentions `.png` or `.svg`; per assignment direction these artifacts are **`.jpg`** exports generated with **Kaleido** for easy submission.

## Data source

- `Week6_files/courtlistener_week5_repull_40k.csv` (39,040 rows; columns include `dataset`, `case`, `judge`, `court`, `court_id`, `date_of_decision`, `cite_count`).
