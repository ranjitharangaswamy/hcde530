# Week 6 — Plotly practice and mini trial questions

Week 6 is **not** the Mini Project submission. Here I practiced Plotly and Dash, and answered **small trial questions** with pandas on the same CourtListener CSV from Week 5.
Disclaimer: Used Cursor agent (AI) for language refinement and editing this week's markdown file.

Week 6 is not the Mini Project submission. I practiced Plotly and Dash on the same CourtListener CSV from Week 5, and answered four small trial questions with pandas counts and charts.

The three Mini Project questions (judges, citations by court level, top cited cases) live in MiniProject1/ only — not repeated here.

### Did these tasks using Cursor, Plotly, and a local venv
1. Worked through Week6_files/plotly-exercises.ipynb (chart type choices, including when 3D misleads).
2. Ran Week6_files/week6_mini_analytics.ipynb: filter, count, and group the CourtListener export.
3. Built three interactive 2D charts in week6_charts.py; exported PNG + HTML to Week6_files/.
4. Revised an earlier 3D draft after feedback — Chart 1 had only three data points after grouping, which is not enough for a 3D scatter.
5. Kept courtlistener_mp1a_dash.py and mp1a_interactive_figures.ipynb as Mini Project tooling (separate from Week 6 grading).

```

## Competencies

### C6 — Data visualization

#### Chart 1 — opinions by year and court (`week6_chart1_opinions_by_decision_year.png`)

Question it answers: How many opinion rows in this Seattle-area download were decided in 2025?

<p>I first tried a 3D scatter (year × court × row count). After grouping the data, only **three** year-and-court combinations remain: 2018 federal (152 rows), 2019 federal (2,888 rows), and 2025 state appeals (~36,000 rows). A 3D chart adds rotation without a real third dimension — it made the counts harder to read, not easier.

Fixed this with a **grouped bar chart**: year on the x-axis, row count on the y-axis, color by court. Each bar is labeled with the count. The main takeaway is visible immediately: this export is almost entirely 2025 state appellate data; federal rows are from earlier years.

—
Personal observation: I check the grouped table before picking a chart. If I had counted only three rows after `groupby`, I should not have reached for 3D in the first place. The chart should match the shape of the summary table, not the raw 39k rows.

#### Chart 2 — criminal vs other captions in 2025 (`week6_chart2_2025_criminal_vs_other_captions.png`)

Question it answers: In 2025, how many cases look like criminal appeals vs everything else?

<p>I flag titles matching **State of Washington v. …** as a rough criminal proxy and compare that group to all other captions. The chart is a **horizontal bar chart** with two bars — about one-third criminal-style, two-thirds other. This is based on title wording, not an official court case-type field.

—
Personal observation: Two categories do not need a third axis. A horizontal bar lets a reader compare lengths directly. I kept the chart interactive (HTML) so hover shows exact counts, but the PNG still tells the story at a glance.

#### Chart 3 — family-law keywords in 2025 (`week6_chart3_2025_family_title_keyword_rows.png`)

Question it answers: In 2025, how many case titles mention family-law words (divorce, custody, guardianship, etc.)?

<p>Very few 2025 rows match those keywords; most do not. Same two-bar horizontal layout as Chart 2. The chart footnote states that keyword matching is a proxy — not a legal classification.

—
Personal observation: A low count here is easy to misread as “no family cases in Washington.” The honest read is “this pull does not surface many family cases **by title**.” I say that in the chart note and in the write-up so the number is not over-interpreted.

#### Interactive export (not 3D)

Static PNGs are in the repo for submission. Matching `.html` files support hover, zoom, and pan in a browser. `Week6_files/week6_charts_interactive.html` stacks all three charts on one page.

—
Personal observation: Interactivity does not require 3D. Plotly 2D charts in HTML are enough for exploration; 3D was visual noise for this dataset.

---

### C5 — Working with data in pandas

#### Four mini trial questions

These are quick sanity-check questions — not the Mini Project citation/judge threads. Each maps to a count or small table in `week6_mini_analytics.ipynb`.

| # | Question | How I answered it |
|---|----------|-------------------|
| 1 | How many opinion rows were decided in **2025**? | Filter by decision year; split count by court. |
| 2 | In **2025**, how many titles mention family-law keywords? | Search case title text; count rows and unique titles. |
| 3 | How many **federal W.D. Wash.** opinions from **2025** are in this file? | Filter 2025 + federal court code (`wawd`). **Answer: 0.** |
| 4 | In **2025**, criminal-style titles vs other captions? | Pattern match on title; compare two groups. |

<p>Question 3 returning zero is a **coverage** result: federal rows in this export are from 2018–2019, not 2025. That is what the file contains, not a broken filter.

—
Personal observation: I run the counts in the notebook first, then chart. Chart 1 is literally a picture of the three-cell table from question 1. If the table and chart disagree, the chart is wrong.

---
**C6 — Visualization:** I built clear 2D Plotly charts (grouped bars and horizontal bars), labeled axes and titles with the main finding, added notes where the data is limited, exported PNGs for submission, and kept interactive HTML versions to explore in a browser. I moved away from 3D charts after getting feedback from the TA.

---
### C7 — Judgment and honest limits
I call out when a question cannot be answered exactly from this file (no federal 2025 rows; “family law” only inferred from titles) and when a chart choice would mislead (for example, 3D on only three data points or two categories).
#### What this file can and cannot say

- The source is CourtListener **opinions**, not a full docket with official case-type codes.
- “Family law” and “criminal” splits use **title text proxies** — rough guesses, not court labels.
- Duplicate rows per caption can inflate counts; Chart 3’s notebook cell also reports unique titles for that reason.
- Question 3 (zero federal 2025 rows) is stated in text, not plotted — there is no variation to visualize.

—
Personal observation: I distrust aggregates that hide their filters. When a stakeholder asks “how many family cases in 2025?” the honest first answer is “depends what you mean and what’s in the export.” Week 6 practice is naming that gap before drawing a chart.

---

## Connection to design / research practice

1. Legal and policy datasets rarely arrive with clean labels ready for a chart. Like survey exports with free text where numbers were expected (Week 3), a CourtListener pull can be **sparse, duplicated, and misaligned with the question** — e.g. searching for 2025 federal rows when the file holds 2018–2019 federal data instead.
2. A chart that looks sophisticated (3D, many points) can still mislead if it does not match the underlying table. Visualization is not decoration; it is an argument. Wrong chart type is the same class of error as wrong sort order on “top 5.”
3. Exporting PNG plus interactive HTML creates an audit trail: anyone can open the HTML, hover for exact counts, and compare to the notebook without re-running code. That matters when a TA or collaborator needs to trust the numbers, not just the picture.
4. Week 6 trial questions are deliberately small — “how many rows in 2025?” — before Mini Project 1 asks harder citation and judge questions. That order mirrors research practice: sanity-check coverage before building personas or policy claims on top.

—

## One thing I want to get better at next

1. **Chart choice before coding.** I want to sketch the aggregated table (row count, number of categories, time vs categorical) and pick the chart type from that — not from what Plotly demo notebooks feature. That would have avoided the 3D detour on Chart 1.
2. **Self-contained chart titles for outsiders.** Titles like “2025 family-law title keyword proxy” are accurate but jargon-heavy. I want each title to read clearly to someone who does not know CourtListener field names.
3. **Separate commit scope.** I pushed Week 6 chart fixes on their own branch so they would not mix with Mini Project 1 work. I want that habit by default — one logical change per commit and per push — so reflection write-ups like this are easier to trace later.

—



