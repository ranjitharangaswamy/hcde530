# Week 5 — First look at structured data (pandas)

```
#What I did this week

1. This week I worked through the Week 5 demos on loading CSVs into pandas, running a repeatable “first look” checklist on my new judgements and jurisdiction-based cases dataset. I merged two related tables on a shared key.
2. I set up a local Python environment the way the course expects: `python3 -m venv .venv`, activate, then install packages inside the venv. That fixed the Homebrew / PEP 668 “externally-managed-environment” error I hit when I tried to `pip install` straight onto the system interpreter.
3. I practiced articulating merge tasks clearly (both DataFrames, the shared column name, inner vs left) so an agent or collaborator does not have to guess — weak prompts like “merge the tables” invite wrong keys or join types.

###Did these tasks using Cursor and Python

1. Ran **week5_pandas_demo.ipynb**: imported pandas, loaded CSVs with `pd.read_csv()`, and stepped through `head`/`tail`, `info`, `describe`, missing counts, `value_counts`, filters, and `groupby` summaries — the standard sequence before trusting any aggregate. Added a **CourtListener bridge** section that runs the five in-class table operations on `courtlistener_firstlook_sample.csv` alongside the app-reviews walkthrough.
2. Ran **week5_merge_demo.ipynb**: loaded `reviews_mini.csv` and `app_info.csv`, merged on `app_id` with `pd.merge()` / `.merge()`, verified row counts, then computed category-level averages — showing how split files become one analyzable table.
3. Built **`week5_courtlistener_cases.ipynb`**: pulled stacked CourtListener search results into pandas (`df_mp1`) and applied the same MP1-style operations to live API data.
4. Documented **PEP 668**: learned why macOS/Homebrew Python blocks global `pip install` and why installs belong in a venv or project environment, not `--break-system-packages` on the system runtime.

```

### Applying the five class operations to my CourtListener dataset

In **`week5_courtlistener_cases.ipynb`** I take several Legal Search results (Seattle federal court, King County appellate court, etc) and **stack them into one table** called `df_mp1`. That way I run the same five class steps on live rows, not only the small practice files.

- **`head()` and `info()`** — I scan real case titles (`caseName`), column types, and how full each column is before I trust any summary. I check whether `judge` or the parsed party fields are often empty.
- **`value_counts()`** — For `dataset` or `judge`, I see which search slice shows up most often and which judge text repeats. The API sometimes returns long or messy judge strings, so counting labels matters before I compare groups.
- **`df[df['_decision_dt'] >= …]`** — I limit rows to decisions on or after a cutoff (for example after 1990-01-01) so I am not mixing old and new cases in one average citation count.
- **`groupby('dataset')['cite_count'].mean()`** — I compare average `cite_count` across those slices. I still read what `cite_count` means in the export before I treat it as “how cited” a case is.
- **`isnull().sum()`** — CourtListener often leaves plaintiff/defendant blank when the title is not a simple “A v. B” style name. `judge` can also be missing on extra rows for the same case. Counting blanks first stops me from reporting group stats that quietly skip or skew incomplete rows.

## Class Insight — externally managed Python (PEP 668)

I did not know my machine’s Homebrew Python counts as an **externally managed environment**. That is why plain `pip install pandas` failed with “externally-managed-environment”: the OS / Homebrew Python is protected so user packages do not overwrite or conflict with what the distributor installed.

**What I learned:** installs belong in a **virtual environment** (`python3 -m venv .venv`, then `source .venv/bin/activate` and `pip install -r requirements.txt`), not on the system interpreter. That matches how this repo’s week 5 setup works and avoids `--break-system-packages`, which is risky on a shared Homebrew Python.

## Competencies

###C3 — Data cleaning & preparation

The Week 5 notebooks treat **understanding structure before summarizing** as non-negotiable. `head()` and `info()` answer “what columns exist and what types are they?” before `describe()` or means mean anything. Checking `isnull().sum()` early surfaces missingness that would otherwise silently distort a mean or a filter.

The merge demo makes the same point at the **table-relationship** layer: neither `reviews` nor `apps` alone answers “average rating by category.” You need an explicit join key (`app_id`), an intentional join type (inner drops non-matches), and a row-count sanity check after the merge. That mirrors research practice where you join a participant roster to a survey export — wrong key or wrong join, wrong story.

#### Personal observation:

I am carrying forward Week 3’s instinct to **not trust aggregates until I know what the rows represent**. Week 5 adds: do not trust a merged table until I know **which rows survived the join** and whether that matches my mental model of “every review matched an app.”

#### Output:

Console and notebook outputs from the demos — shapes, heads, merged preview, and grouped summaries form an audit trail. They are quick to re-run after changing a filter or a file version.

###C4 — APIs and data acquisition

Week 5’s CourtListener work sits **downstream of acquisition**: the rows in `df_mp1` are not a hand-made CSV — they are **stacked search / export results** from CourtListener (the same API family I used in Week 4 with the official client and token). That means the pandas “first look” is always a second step: the table inherits whatever the search returned (slice, court, date window) and whatever fields the API exposes (`caseName`, `cite_count`, `judge`, etc.).

**Evidence in this repo:** **`week5_courtlistener_cases.ipynb`** — I load multiple result sets, stack them, and keep a `dataset` (or similar) label so I can still tell which search each row came from after they sit in one DataFrame. That is acquisition literacy in practice: I need to know **provenance** (which query produced this row) before I compare means across groups.

**What carries over from Week 4:** authentication and rate-limit awareness are not visible inside every notebook cell, but they still matter — if I change how I pull or how often I pull, the stacked file changes and every downstream `groupby` changes with it.

#### Personal observation:

I used to think of “API week” and “pandas week” as separate skills. Week 5 makes the link explicit: **bad or vague acquisition** (overlapping searches, mixed jurisdictions, no row-level label for source) makes even correct pandas code tell a fuzzy story. Labeling slices when I stack is the same discipline as naming variables in a survey export.

#### Output:

Stacked table in `df_mp1`, plus saved or printed intermediate exports where I kept a copy of what I pulled — so the notebook is reproducible as “acquire → stack → first look,” not only “read_csv and pray.”

###C5 — Data analysis with pandas

**What it means:** Using pandas to answer a concrete question about a dataset and not just loading it. That includes filtering rows, grouping, aggregating, and noticing missing values. It also means picking the pandas step that matches the question and saying what the numbers mean in plain language, not only pasting output.

**Evidence in this repo**

| Requirement | Where / how |
|-------------|-------------|
| Notebook or script loads data and answers at least one specific analytical question | **`week5_courtlistener_cases.ipynb`**: after stacking pulls into `df_mp1`, I filter to decisions on or after 1990-01-01 and compare **mean `cite_count` by `dataset`** slice — that answers whether citation counts differ across the Seattle federal Court, and King County appellate samples in one window. **`week5_merge_demo.ipynb`**: merge reviews to app metadata, then **average rating by `category`** — answers “which product category scores lowest on average?” |
| At least two pandas operations (examples: `groupby`, `fillna`, `value_counts`, `merge`) | **`merge`** + **`groupby`** on merged reviews; **`groupby`** + mean on `df_recent_window`; **`isnull`**, **`value_counts`**, and date **filter** on `df_mp1` (see bullets above and Part 2 in the CourtListener notebook). |
| Written interpretation — what the result means, not only the table | Below. |

After restricting to decisions on or after 1990-01-01, mean `cite_count` is not the same across every `dataset` slice in `df_mp1`. That gap **depends on** what CourtListener counts as a “cite” and on how many rows each search returned — so I treat it as a prompt to compare slice sizes and missing `judge` / party fields before I explain *why* one slice looks higher or lower. I wrote that caution in this file and in the notebook comments as a reminder to **dig into coverage next** (for example duplicate case rows or short samples) instead of treating one mean as a headline.


## Connection to design / research practice

1. **First-look discipline** matches how I skim a dataset before writing a finding: variable types, missingness, and value distributions prevent headline numbers that rest on hidden junk rows.
2. **Merging** is the computational version of linking a codebook to raw exports — same requirement for a stable identifier and explicit rules for unmatched rows.
3. **Isolated environments** parallel reproducibility in research: my laptop’s system Python is not a portable specification; a venv or requirements list is.

## One thing I want to get better at next

1. Automating a short “data card” output after every load — shape, dtypes, null rates, and duplicate keys on merge columns — so the audit trail is one glance instead of re-reading cells.
2. Naming merge keys and suffix conventions when both tables repeat column names after join, so later analysis does not reference ambiguous `_x` / `_y` columns by mistake.

—

