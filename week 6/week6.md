# Week 6 — MP1a CourtListener visualizations (Dash + Plotly)

```
#What I did this week

1. I turned the stacked CourtListener export (I had saved my API data on a csv file which has ~39k rows) into **three interactive Plotly charts** that each answer **one** of my MP1a analytical questions, wrapped in a small **Dash** app with **Dash Mantine Components** for layout, alerts, and typography.
2. I kept the browser work light on purpose, where heavy charts aggregate to roughly **45–48 plotted points** (month × court buckets; top-45 case titles) and the titles say how many rows the full CSV has — so a reader is not misled into thinking every dot is one opinion row.
3. I hit the same **PEP 668** constraint as Week 5 when I tried to install Kaleido on the system Python. I fixed it the same way the course expects: **`python3 -m venv` inside `week 6/.venv`**, then `pip install` there, then run the Dash script with **`week 6/.venv/bin/python`** so exports and the server share one interpreter. (This took some back and forth googling and chatgpt research to save tokens)
4. I exported **static `.jpg` files** with Kaleido for the rubric (the writeup allows PNG/SVG; the MP1a direction I followed was JPG) and committed them next to the script so the repo is the evidence trail, not only a screenshot on my desktop.

###Did these tasks using Cursor and Python

1. Built **`courtlistener_mp1a_dash.py`**: loads the CSV with **pandas**, builds Plotly figures (**`scatter_3d`** for questions **(a)** and **(b)**, horizontal **`bar`** for **(c)**), composes them inside **`dmc.MantineProvider` → `Container` → `Stack` / `SimpleGrid` / `Card` / `Alert` / `Paper` / `Tooltip` / `Badge` / `RingProgress`**, and runs locally on `127.0.0.1:8050`.
2. Wrote **`--export`**: calls `fig.write_image(..., format="jpg")` for **`mp1a_chart1_court_level_cites_3d.jpg`**, **`mp1a_chart2_top_cited_cases_wd_wash.jpg`**, **`mp1a_chart3_top_authority_titles.jpg`** into the **`week 6/`** folder.
3. Used **Cursor** to iterate on layout (for example: `dmc.Card` rejected a `span=` prop — I moved the full-width third chart into a vertical `Stack` under a `SimpleGrid` instead of guessing Mantine’s API).
4. I wired **Dash callbacks** from **Mantine `Select` / `SegmentedControl` / `Slider`** inputs to **pandas → Plotly** for charts **(b)** and **(c)** so those views re-render from UI state (not only hover/zoom on a static figure).

```

## Three charts ↔ three MP1a questions (short map)

| Question | Committed JPG | Chart type | What it encodes (light slice) |
|----------|---------------|------------|--------------------------------|
| (a) Judges / citations **and** court **level** | `mp1a_chart1_court_level_cites_3d.jpg` | **3D scatter** | Month × court stratum × **mean `cite_count`**; size = opinion count in bucket (capped **48** points) |
| (b) Most cited judgments in a **specific jurisdiction** | `mp1a_chart2_top_cited_cases_wd_wash.jpg` | **3D scatter** (live app) | Rank × cite metric (max/mean per title) × **row count** per title; Mantine **Select / SegmentedControl / Slider** + **Badges**; JPG is a static camera angle |
| (c) **Average** cite clusters per opinion + dominant case titles | `mp1a_chart3_top_authority_titles.jpg` | **Horizontal bar** | **Top 45** titles by **`sum(cite_count)`**; color shows how many CSV rows each title has; title states **dataset mean** (~0.152) |

**Honest null (still a finding):** every **`washctapp`** row in this pull has **`cite_count = 0`** and **`judge` is missing** on the state slice, so “court level” contrast is extreme and judge ranking only makes sense on the **federal** rows. I say that in the Dash **`Alert`** and in the competency section below instead of pretending the state chart carries citation signal.

## Competencies

###C2 — Code literacy and documentation

**What counts as evidence:** docstrings / module docstring, a markdown file a TA can read without running the server, and commit language that says what shipped.

**Strong claim (specific):** The module docstring at the top of **`courtlistener_mp1a_dash.py`** states the CSV path, how to run the server, and how to run **`--export`** — that is the “future me” note I wanted because Dash wiring is easy to forget. This **`week6.md`** is the non-code reader path: chart titles, file names, and the PEP 668 / venv run command live here on purpose, not buried in chat.

**Weak claim (what I avoided):** “I documented my work.” (No pointer to which file proves it.)

####Personal observation:

I still catch myself wanting to describe the app as “self-explanatory” because the charts look finished. The rubric is asking for **chart justifications**, which are really **arguments**: why chart **(b)** became a **3D scatter** (rank × cite metric × duplicate-row depth) after aggregation, why chart **(c)** stays a **horizontal bar** for long case names, why `max` vs `sum` differ between questions **(b)** vs **(c)**. Writing those down in prose next to the committed JPGs keeps me honest about **what the chart cannot prove** (and that a JPG cannot spin).

####Output:

- **`week 6/week6.md`** (this file) + **`week 6/courtlistener_mp1a_dash.py`** + the three **`mp1a_chart*.jpg`** files in the same folder.

###C3 — Data cleaning and file handling

**What counts as evidence:** a script that reads a real CSV, handles a real structural problem, and explains skewed output instead of crashing or lying.

**Strong claim (specific):** I **`read_csv`** from **`Week6_files/courtlistener_week5_repull_40k.csv`**, parse **`date_of_decision`** with **`errors="coerce"`**, normalize **`judge`** strings to `pd.NA` when they are blank/`"nan"`, and map **`court_id`** to a human-readable **`court_level`** label before any aggregation. The “cleaning” story that mattered most this week was **coverage**, not typos: **`isnull().sum()` on `judge` is ~36k** in a ~39k row file, and **`cite_count` is identically 0 on all `washctapp` rows** — so any chart that blended courts without labeling would **look** like “citations are rare everywhere,” which is false for **`wawd`**.

**Weak claim:** “I cleaned the CSV.” (Does not say what was broken or how you detected it.)

####Personal observation:

Week 3 taught me to distrust aggregates until I know the rows. Week 6 adds: distrust **pretty charts** until I know **which slice carries the signal**. A flat zero column is not “clean data” — it is a **finding about the pull or the field**, and it belongs in the write-up, not brushed under a rug.

####Output:

Console-free evidence is the **figures themselves**: the Wash. Ct. App. stratum in chart 1 sits at **mean cite = 0** across months; chart **(b)** defaults to **W.D. Wash.** (`wawd`) because the state slice has no cite signal to rank in **this** extract (you can still switch the Mantine **Select** to `washctapp` and see the flat cloud).

###C4 — APIs and data acquisition

**What counts as evidence:** tying the table in hand back to **how it was acquired**, and not committing secrets.

**Strong claim (specific):** The rows in **`courtlistener_week5_repull_40k.csv`** are **downstream of the CourtListener search / export path** I already documented in **`week5_courtlistener_cases.ipynb`** (stacked pulls, labeled `dataset` / `court_id`). I did **not** embed new API calls inside the Week 6 Dash file — the artifact is the **saved CSV** — but the **provenance story** is the same Week 4 / Week 5 lesson: if I change the query or the date window, every aggregate in charts 1–3 moves. No token lives in this week’s script; keys stay in **`.env`** / gitignored patterns from earlier weeks.

**Weak claim:** “I used CourtListener data.” (No link between acquisition choices and what the charts can say.)

####Personal observation:

I used to treat “visualization week” as disconnected from “API week.” This assignment is the opposite: **the citation field is only interpretable after I remember what the API returned and how rows duplicate per case title** (for example the same title repeating at the same max cite).

####Output:

Upstream notebook evidence: **`week5_courtlistener_cases.ipynb`**. Week 6 consumption evidence: **`courtlistener_mp1a_dash.py`** + CSV path in the module docstring.

###C5 — Data analysis with pandas

**What it means:** asking a concrete question, picking **`groupby` / `agg` / filters`** that match the question, and saying what the number means — not only printing it.

**Evidence in this repo**

| Requirement | Where / how |
|-------------|-------------|
| Loads data and answers specific analytical questions | **`courtlistener_mp1a_dash.py`**: `load_df()` reads the CSV; `agg_monthly_court_cites()` answers **(a)** over time by court; `_q2_case_frame()` / `fig_q2_scatter3d_jurisdiction()` answers **(b)** by court slice + rank + cite vs row depth; `fig_q3_top_authorities()` groups by **`case`** with **`sum` / `count`** for **(c)**. |
| At least two pandas operations | **`groupby` + `agg`** on month/court; **`groupby` + `max`** on case titles within a court; **`groupby` + `sum`/`count`** on case titles dataset-wide; date parsing via **`to_datetime`**. |
| Written interpretation (meaning, not only tables) | Chart **titles** carry the headline numbers (means, caps like “45 titles”, “48 buckets”); this markdown calls out the **Wash. Ct. App. all-zero** pattern and why chart 2 scopes to **W.D. Wash.** |

**Strong read on the numbers:** mean **`cite_count` per row** is **~0.152** because **36,000 / 39,040** rows are the state slice at **0** cites in this pull. That is why question **(c)** uses **both** a scalar mean (in the chart title / text card) **and** a **tail-heavy bar** for titles that still concentrate cite mass on the federal side.

**Weak read:** “The average was low.” (No tie to row mix or court_id.)

####Personal observation:

`groupby('case')` taught me to decide whether “most cited authority” for this file should be **`max`** per title (question **b**, jurisdiction slice) vs **`sum`** across duplicate rows (question **c**, dataset-wide mass). Those are two different definitions; picking both deliberately is pandas literacy, not an accident.

####Output:

The **`--export`** path regenerates the same figures the Dash server shows — same pandas pipeline, no second truth.

###C6 — Data visualization

**What it means:** matching **chart type to data shape** and writing a **justification** a reviewer can argue with.

**Evidence in this repo**

| Chart | Why this type (not something else) |
|-------|-------------------------------------|
| Chart 1 (3D) | I needed **time × court stratum × mean cites** in one view after **collapsing** to dozens of points; a 2D line chart could show time, but separating **two courts** without overplotting got clearer once size encoded **opinion_count** in-month. |
| Chart 2 (3D) | **Rank × cite metric × row-count** separates “one loud row” from “many duplicate rows” for the same caption; color reinforces the cite metric. |
| Chart 3 (horizontal bar) | **Long categorical labels** (`case` titles). Vertical bars would truncate titles; horizontal bars keep the **unit** (`cite_count` sums) on the x-axis where it is easy to compare. |
| Color on chart 3 | Encodes **`opinion_rows`** so a big bar is not automatically “one opinion” — it might be **many duplicate rows** for the same caption, which is a visualization honesty choice. |

**Weak claim:** “Plotly made nice charts.” (No defense of chart type vs question.)

####Personal observation:

3D is easy to abuse. I only kept it because the **point count is capped** and the axes state **month**, **court code**, and **mean cite_count** — otherwise it becomes chart junk. If I had plotted 39k raw rows in 3D, I would be violating my own Week 5 “first look” instinct.

####Output:

Committed **`.jpg`** artifacts in **`week 6/`** plus interactive **`dcc.Graph`** objects in the Dash app.

###C7 — Critical evaluation and professional judgment

**What it means:** catching outputs that are **technically runnable** but **misleading**, and correcting before submission.

**Strong claim (specific):** An early layout idea was to put **judge strip plots** in as a third “pretty” chart. That would have **muddled the rubric** (“each chart answers a **different** question”) because judges only exist on **`wawd`**. I cut that as a standalone figure and instead put **top federal judges by mean cite** in a **Mantine text card** under the charts, with an **`Alert`** that states the **all-zero Wash. Ct. App. cite field** plainly — that is the “I would not show this to a stakeholder without a caveat” moment, handled explicitly.

**Weak claim:** “I checked the charts.” (No example of what was wrong and what you changed.)

####Personal observation:

Cursor / codegen is helpful for Dash boilerplate, but it happily invented invalid component kwargs until I ran an import test. That is the same pattern as Week 3: **run the code**, read the **`TypeError`**, adjust — not ship the first answer because it “looks right” in chat.

####Output:

A runnable **`courtlistener_mp1a_dash.py`** where the layout matches Mantine’s actual prop surface, and prose here that documents **null findings** as findings.

## Connection to design / research practice

1. **Provenance first:** the same way I would not quote a usability stat without knowing which session file it came from, I should not quote a “citation” stat without naming **which court_id slice** and whether **`cite_count` is populated** there.
2. **Long labels are a UX problem:** legal case titles behave like open-ended survey verbatims — the visualization choice has to prioritize **readability**, not only default chart templates.
3. **Flat metrics are still results:** if a stakeholder asks “how cited are King County appellate opinions in this pull?” the correct answer is “**zero in this file’s `cite_count` column**,” not a prettier chart that hides the emptiness.

## One thing I want to get better at next

1. **Pin dependencies** for Week 6 in a tiny `requirements-week6.txt` (or a lock file) so “install dash + dmc + kaleido” is one copy-paste for a grader, not only implied by my venv.
2. **Automate a one-page “data card”** after `read_csv` — shape, `% missing judge`, min/mean/max `cite_count` **by `court_id`** — and render it as a Mantine **`Table`** above the charts so the caveats are visible even if someone never opens this markdown file.

—

## Notes / quotes / links

- Source table: **`week 6/Week6_files/courtlistener_week5_repull_40k.csv`**
- Interactive app: **`week 6/courtlistener_mp1a_dash.py`** (Dash + [Dash Mantine Components](https://www.dash-mantine-components.com/getting-started) + Plotly)
- Static submissions: **`week 6/mp1a_chart1_court_level_cites_3d.jpg`**, **`week 6/mp1a_chart2_top_cited_cases_wd_wash.jpg`**, **`week 6/mp1a_chart3_top_authority_titles.jpg`**
- Run commands (repo root):

```bash
"week 6/.venv/bin/python" "week 6/courtlistener_mp1a_dash.py"
"week 6/.venv/bin/python" "week 6/courtlistener_mp1a_dash.py" --export
```

## Data appendix — Week 6 artifacts

| Artifact | Role |
|----------|------|
| `Week6_files/courtlistener_week5_repull_40k.csv` | Input: stacked CourtListener-style rows (`court_id`, `cite_count`, `judge`, etc.). |
| `courtlistener_mp1a_dash.py` | Loads CSV, aggregates in pandas, builds Plotly figures, wraps UI in DMC, optional JPG export. |
| `mp1a_chart*.jpg` | Rubric-facing static captures of the three figures. |
| `week6.md` | Competency mapping + chart justifications + null findings. |

—
