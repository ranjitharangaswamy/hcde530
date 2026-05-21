# Mini Project 1 — CourtListener Citation Analysis

**Student:** Ranjitha Rangaswamy  
**Project:** `Miniproject1.ipynb`, `data/courtlistener.csv`

---

## What do these terms mean?

Short glossary for non-legal and non-technical readers. The notebook uses the same terms in Section 1 — Overview.

| Term | Explanation in non-legalese or plain English |
|------|------------------|
| **CourtListener** | A free public database of court opinions — like a searchable legal library. |
| **Opinion / `case` (title)** | One court decision; `case` is the case name (caption). |
| **Citation / `cite_count`** | How often **other** cases reference **this** opinion in this export (incoming cites). Not how many cases this opinion cites. See [What does `cite_count = 0` mean?](#what-does-cite_count--0-mean) below. |
| **W.D. Wash. / `wawd`** | **W**estern **D**istrict of **Wash**ington — a **federal** trial court for western Washington. Data code: `wawd`. |
| **`washctapp`** | **Wash**ington **Court of Appeals** — a **state** appellate court. Data code: `washctapp`. |
| **King County pull** | State-side rows from a Seattle / King County–oriented search in CourtListener. |
| **Federal vs state** | Different court systems; do not compare their cite numbers without labeling which court you mean. |
| **`court_id` / `court_level`** | Short codes and readable labels for which court an opinion came from. |
| **Jurisdiction** | Which court’s territory you are analyzing (here, often federal W.D. Wash.). |
| **Judge / `judge_clean`** | Authoring judge when listed; reliable mostly on federal rows in this file. |
| **Citator** | Professional citation-research software; this project is exploratory, not a full citator. |

### What does `cite_count = 0` mean?

In this file, `cite_count` counts **incoming** citations: other decisions that point **at** this opinion in CourtListener’s export. It is **not**:

- how many cases this opinion cites (outgoing), or  
- a guarantee about “lower courts only” — just a general “cited by others” number from this pull.

When a row shows **`cite_count = 0`**, that means **this dataset field is zero for that opinion** — not that you can prove the opinion was never cited anywhere in the real world.

It could mean:

1. CourtListener truly recorded few or no incoming cites for that opinion in this export, or  
2. Cite data is **missing or not filled in** for that court slice (what this project argues for most `washctapp` / state appellate rows).

**It does not automatically mean** “this opinion was never cited by anyone, ever.”

**Why so many zeros in this project:** Roughly 92% of rows are Washington Court of Appeals (`washctapp`). In this pull, **every** state row has `cite_count = 0`, while federal Western District of Washington (`wawd`) rows often have non-zero values. That pattern points to a **data coverage gap on the state side**, not to “Washington appellate opinions are never cited.”

Zero does **not** mean this case failed to cite other people. That would be outgoing citation, and this column only tracks incoming citation. Zero also does **not** prove that no other court ever cited the case in real life. It only means CourtListener counted none in this export, which is a much weaker claim. What you can say safely is simpler: for `washctapp`, the cite field is effectively empty in this file, so you should not rank “most cited” state cases from it. In this CSV, meaningful citation signal shows up mainly on the federal `wawd` slice.

---

<!-- Chart explanations (plain English) — matches static images in images/ and Plotly cells in Miniproject1.ipynb -->

<!-- Chart 1 (mp1a_chart1_court_level_over_time.jpg): Dual line chart of average citations per month, with one line for federal district court opinions and one for state appellate opinions. The federal line moves above zero as months progress; the state line stays flat on zero. This shows that "how cited" opinions look in this dataset depends heavily on which court you are looking at, not on one number for the whole file. -->

<!-- Chart 2 (mp1a_chart2_top_cited_cases_wd_wash.jpg): 3D scatter of the most cited case titles in Western District of Washington. Each point is a case title; height and color reflect how strongly it is cited and how many duplicate rows exist in the export. Big tiles at the top are the titles lawyers would notice first as heavily cited in this federal slice. -->

<!-- Chart 3 (mp1a_chart3_top_authority_titles.jpg): Treemap where bigger, warmer-colored rectangles are case titles that account for more total citation mass in the whole dataset. A few large blocks dominate the view; many smaller blocks sit around them. Tile color runs from cool to hot by total cites (Turbo scale) so high-mass titles stand out. This answers "where does citation weight pile up?" differently from a bar chart — you see share of the whole at a glance. -->

---

## Section 4 — Conclusions

What would you tell someone based on this analysis? Plain-language answers to each research question — findings, not code.

### Question 1 — Do citations vary by court level (and judges)?

**What I found:** In this file, only the federal Western District of Washington (`wawd`) rows show real movement in `cite_count` over time. The state Court of Appeals (`washctapp`) rows sit at zero for every month in the chart. Judge names are mostly missing on the state side, so “which judge is most cited” only makes sense on the federal slice.

**What it suggests:** You cannot describe “Washington opinions” as a single group in this export. Citation signal is a **federal-court story here**, not a blended state-plus-federal average. Anyone using this data for research or design needs a visible court label before they trust a cite number.

**What I would investigate next:** Whether CourtListener has a different citation field for state opinions; a federal-only judge ranking with clear population notes; and whether monthly buckets hide year-to-year noise because the pull mixes many decision years.

### Question 2 — What are the most cited judgments in Western District of Washington?

**What I found:** Within `wawd`, citation strength is concentrated at the top — a relatively small set of case titles shows the highest max cites, and some titles appear on many duplicate rows in the export. The 3D view is useful for spotting that steep “head” of well-cited captions, not for reading exact ranks without the pandas table.

**What it suggests:** For this federal district in this snapshot, a lawyer or researcher would start with a short list of dominant titles rather than assuming cites are spread evenly. It is a **starting bibliography**, not proof of how a title ranks nationwide or over all time.

**What I would investigate next:** Deduplicating rows that share the same `case` caption; comparing max vs mean cite per title; and checking a few top titles in a professional citator to see if the export’s counts match real-world use.

### Question 3 — What is average cite behavior, and which titles hold the most citation mass?

**What I found:** The average cite count per row across the whole file is very low (about 0.15) because roughly 36,000 state rows are zero. The treemap shows that **total** citation mass still piles onto a handful of case titles — often the same federal-heavy names — even when the “typical row” looks barely cited.

**What it suggests:** “Average opinion” and “most important titles” are different questions. Reporting only a global mean would understate how much weight sits on a few decisions. A treemap makes that imbalance visible: a few large tiles carry most of the summed cites.

**What I would investigate next:** Reporting means **by court** side by side; filtering the treemap to federal-only rows; and documenting how CourtListener defines a “cite cluster” so readers know what `cite_count` actually counts.

### Overall takeaway

The main lesson from this project is labeling: **who the rows belong to (which court) matters more than any single chart.** After profiling the data, the honest story is federal citation variation in `wawd`, a flat zero line for `washctapp` in this pull, and concentrated citation mass on a small set of titles — not one universal “most cited Washington opinion” from the full CSV.

---

## Section 5 — Process

How I arrived at the final Mini Project — details that are not obvious from the notebook and images alone.

**Building the dataset:** The file did not come from one click. Earlier in the course I stacked CourtListener API searches from Weeks 4–5 (federal W.D. Wash. and a King County / state appellate pull) into one CSV for analysis. For submission I copied that file and the chart code into a standalone `MiniProject1/` folder so graders only need one directory.

**Pivot that changed the story:** My first instinct was to treat ~39,000 rows as one population and ask “what are the most cited Washington opinions?” Profiling with `info()`, `describe()`, and `isnull()` showed that **every** `washctapp` row has `cite_count = 0` and that judges are missing on most rows. That was the most important turn — I rewrote the questions, conclusions, and chart titles so they compare **labeled court slices** instead of implying one aggregate for the whole file.

**Visualization iterations:** I started with 3D scatters for all three questions, then replaced Chart 1 with a violet/orange **line chart** (easier to read than a rotating 3D scene) and Chart 3 with a **Turbo-colored treemap** after feedback that bar-style views were hard to read and not colorful enough. Chart 2 stayed a 3D scatter for the jurisdiction question because rank, cite strength, and duplicate-row depth still read well together. I regenerated static JPGs whenever the Python figures changed so `images/` matches `Miniproject1.ipynb`.

**Tooling and AI:** I used pandas in the notebook for tables, `mp1_charts.py` for Plotly figures, Kaleido for exports, and an optional Dash app (`mp1_dash.py`) for interactive sliders. Cursor helped with Dash layout and boilerplate; runtime errors (for example invalid Mantine props) still required manual fixes. AI suggested extra judge-focused charts — I dropped them so **one chart maps to one MP1a question** and the narrative stays focused.

**What I did not lose, but what took time:** I did not restart from scratch, but I did rework conclusions twice after the slice-quality discovery. Aligning the notebook to the course template (Sections 1–5, glossary, pandas cells per question) and syncing `mp1.md` with the final charts was the last pass before submission.

---

## Competency Claims

### C3 — Data cleaning and file handling

I loaded a ~39k-row CourtListener CSV into pandas, parsed `date_of_decision`, derived `court_level` and `judge_clean`, and documented missing judges (36,152 nulls) and uniformly zero `cite_count` on the state (`washctapp`) slice before aggregating. I treated duplicate case captions and court-mixed rows as data-quality constraints that shape which questions the analysis can answer honestly.

### C5 — Data analysis with pandas

I answered all three MP1a questions with pandas `groupby` tables in the notebook (monthly mean cites by court, top Western District of Washington / `wawd` titles by max cite, dataset-wide sum of cites by case) and cross-checked those results against Plotly charts built in `mp1_charts.py`. The analysis separates federal (`wawd` = W.D. Wash.) and state (`washctapp` = Wash. Court of Appeals) populations instead of pooling a misleading global mean.

### C6 — Data visualization

I built three finding-oriented visualizations (violet/orange dual line chart for court level over time, 3D scatter for jurisdiction ranking, Turbo-colored treemap for authority-title citation mass) with labeled axes and titles that state claims, not just variable names. I exported static JPGs to `images/` and provided an interactive Dash app (`mp1_dash.py`) for exploration aligned with the Plotly Dash gallery pattern.

### C7 — Critical evaluation and professional judgment

I interpreted results with explicit limitations: this extract is not a full citator, state cite fields may be incomplete, and 3D/JPG views are exploratory. I revised conclusions after discovering that ~92% of rows are state opinions with `cite_count = 0`, and I documented what practitioners can and cannot conclude from these metrics.
