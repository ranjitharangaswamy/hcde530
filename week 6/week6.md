# Week 6 — MP1a CourtListener visualizations (Dash + Plotly)

```
#What I did this week

1. I took my stacked CourtListener export (~39k rows in a CSV from the API) and built three interactive Plotly charts. Each chart answers one of my MP1a questions. I put them in a small Dash app and used Dash Mantine Components for layout, alerts, and type.

2. I kept the charts light in the browser on purpose. The heavy charts aggregate down to about 45–48 points (month × court buckets; top 45 case titles). The titles say how many rows the full CSV has so nobody thinks every dot is one opinion row.

3. Same PEP 668 issue as Week 5 when I tried to install Kaleido on the system Python. I fixed it the way the course expects: `python3 -m venv` in `week 6/.venv`, pip install there, then run the Dash script with `week 6/.venv/bin/python` so exports and the server use the same interpreter. I had to google around and use ChatGPT a bit to save tokens.

4. I exported static `.jpg` files with Kaleido for the rubric (writeup allows PNG/SVG; MP1a asked for JPG). I committed them next to the script so the repo shows what I turned in, not just a screenshot on my desktop.

###Did these tasks using Cursor and Python

1. Built `courtlistener_mp1a_dash.py`: pandas loads the CSV, Plotly builds the figures (`scatter_3d` for (a) and (b), horizontal `bar` for (c)), Mantine wraps layout and the local server is `127.0.0.1:8050`.

2. Added `--export`: `fig.write_image(..., format="jpg")` writes `mp1a_chart1_court_level_cites_3d.jpg`, `mp1a_chart2_top_cited_cases_wd_wash.jpg`, `mp1a_chart3_top_authority_titles.jpg` into `week 6/`.

3. Used Cursor to fix layout bugs. Example: `dmc.Card` did not like a `span=` prop, so I put the full-width third chart in a vertical `Stack` under the `SimpleGrid` instead of fighting Mantine’s API.

4. Dash callbacks hook Mantine `Select`, `SegmentedControl`, and `Slider` into pandas → Plotly for charts (b) and (c) so those views update from the UI, not only from hover/zoom on a static figure.

```

## Three charts ↔ three MP1a questions (short map)

| Question | Committed JPG | Chart type | What it encodes (light slice) |
|----------|---------------|------------|--------------------------------|
| (a) Judges / citations **and** court **level** | `mp1a_chart1_court_level_cites_3d.jpg` | **3D scatter** | Month × court stratum × **mean `cite_count`**; size = opinion count in bucket (capped **48** points) |
| (b) Most cited judgments in a **specific jurisdiction** | `mp1a_chart2_top_cited_cases_wd_wash.jpg` | **3D scatter** (live app) | Rank × cite metric (max/mean per title) × **row count** per title; Mantine **Select / SegmentedControl / Slider** + **Badges**; JPG is a static camera angle |
| (c) **Average** cite clusters per opinion + dominant case titles | `mp1a_chart3_top_authority_titles.jpg` | **Horizontal bar** | **Top 45** titles by **`sum(cite_count)`**; color shows how many CSV rows each title has; title states **dataset mean** (~0.152) |

**Null finding:** In this pull, every `washctapp` row has `cite_count = 0` and `judge` is missing on the state slice. So “court level” looks extreme and judge ranking only really works on the federal rows. I say that in the Dash `Alert` and below instead of pretending the state chart shows citation signal.

## Competencies

###C2 — Code literacy and documentation

The module docstring at the top of `courtlistener_mp1a_dash.py` lists the CSV path, how to start the server, and how to run `--export`. I wrote it for future me because Dash wiring is easy to forget. This `week6.md` is for someone who opens the repo without running the app: chart titles, filenames, and the PEP 668 / venv commands live here instead of only in chat history. Commits bundle the script, the three `mp1a_chart*.jpg` files, and this writeup so the trail matches what I turned in.

####Personal observation:

The charts look finished enough that I want to call the app self-explanatory. The assignment still wants chart justifications — why (b) is a 3D scatter (rank × cite metric × duplicate-row depth), why (c) stays a horizontal bar for long case names, why `max` vs `sum` for (b) vs (c). Writing that next to the JPGs keeps me honest about what a chart cannot prove.

###C3 — Data cleaning and file handling

####Missing judges and messy strings

I `read_csv` from `Week6_files/courtlistener_week5_repull_40k.csv`, parse `date_of_decision` with `errors="coerce"`, normalize blank or `"nan"` judge strings to `pd.NA`, and map `court_id` to a readable `court_level` before aggregating. `isnull().sum()` on `judge` lands around 36k in a ~39k row file, so the “cleaning” story this week was coverage more than typos.

####State appellate cites all zero

Every `washctapp` row in this pull has `cite_count = 0`. If I mixed courts in one chart without clear labels it would read like citations are rare everywhere, which is not what `wawd` shows.

Chart 1 puts Wash. Ct. App. at mean cite = 0 by month. Chart (b) defaults to W.D. Wash. (`wawd`) because the state slice has nothing useful to rank by cites in this extract; you can still switch the Mantine Select to `washctapp` and see the flat cloud.

####Personal observation:

Week 3 got me to distrust aggregates until I know the rows. Week 6 adds distrusting a pretty chart until I know which slice carries signal. A column of all zeros is a finding about the extract, not something to hide in the write-up.

###C4 — APIs and data acquisition

The rows in `courtlistener_week5_repull_40k.csv` come from the CourtListener search / export path I already walked through in `week5_courtlistener_cases.ipynb` (stacked pulls, `dataset` / `court_id`). The Week 6 Dash script does not call the API again — it reads the saved CSV — but if I change the query or date window, charts 1–3 all move with it. I did not put API keys in the Week 6 script; keys stay in `.env` and gitignored patterns like earlier weeks.

####Personal observation:

I used to treat visualization week as separate from API week. Here they are tied: I can only read `cite_count` sensibly if I remember what the export contains and how rows duplicate per case title (same caption repeating at the same max cite, etc.).

Notebook trail: `week5_courtlistener_cases.ipynb`. Week 6 code + path note: `courtlistener_mp1a_dash.py` (module docstring).

###C5 — Data analysis with pandas

Each MP1a question maps to a pandas path in `courtlistener_mp1a_dash.py`, not only a printed table. Rough map:

| Question / requirement | Where / how |
|-------------|-------------|
| Loads data and answers the three analytical questions | `load_df()` reads the CSV; `agg_monthly_court_cites()` does (a) over time by court; `_q2_case_frame()` / `fig_q2_scatter3d_jurisdiction()` does (b) by court slice + rank + cite vs row depth; `fig_q3_top_authorities()` groups by `case` with `sum` / `count` for (c). |
| Multiple pandas operations | `groupby` + `agg` on month/court; `groupby` + `max` on case titles within a court; `groupby` + `sum` / `count` dataset-wide; `to_datetime` on dates. |
| Interpretation in words, not only tables | Chart titles carry means and caps (“45 titles”, “48 buckets”); this file calls out the Wash. Ct. App. all-zero pattern and why chart (b) scopes to W.D. Wash. |

Mean `cite_count` per row is ~0.152 because a big chunk of rows (~36k / 39,040) are the state slice at 0 cites in this pull. That is why (c) shows both a scalar mean in the title / text card and a tail-heavy bar for titles that still stack cite mass on the federal side.

####Personal observation:

`groupby('case')` made me pick definitions: for (b) inside a court I use `max` per title; for (c) dataset-wide I use `sum` across duplicate rows. Same word “authority” in the prompt, two different meanings; I kept both on purpose.

`--export` rebuilds the same figures the server shows — one pandas pipeline, not a second hidden copy.

###C6 — Data visualization

| Chart | Why this type |
|-------|---------------|
| Chart 1 (3D) | Time × court stratum × mean cites after collapsing to dozens of points. A 2D line could show time, but separating two courts without a mess of overlap got easier once size carried `opinion_count` in-month. |
| Chart 2 (3D) | Rank × cite metric × row-count splits “one loud row” from “many duplicate rows” for the same caption; color backs up the cite metric. |
| Chart 3 (horizontal bar) | Long `case` titles. Vertical bars would clip labels; horizontal bars keep `cite_count` sums on the x-axis where they are easier to compare. |
| Color on chart 3 | Encodes `opinion_rows` so a tall bar is not automatically one opinion — it can be many duplicate rows for the same caption. |

####Personal observation:

3D is easy to overuse. I only kept it because the bucket count is capped and the axes say month, court code, and mean `cite_count`. Dumping 39k raw rows into 3D would go against the same first-look instinct I had in Week 5.

Static JPGs sit in `week 6/`; the live app uses `dcc.Graph` for the same figures.

###C7 — Critical evaluation and professional judgment

####Judge strip plot (cut)

I almost added judge strip plots as a third flashy chart. Judges only really exist on `wawd` in this file, so a third standalone judge chart would have stepped on “each chart answers a different question.” I dropped it as its own figure and put top federal judges by mean cite in a Mantine text card under the charts, plus an `Alert` that states the Wash. Ct. App. cite field is all zeros — the situation where I would caveat before showing a stakeholder.

####Mantine props vs Cursor output

Cursor sped up Dash boilerplate, but it also suggested invalid component kwargs until I ran the code. Same pattern as Week 3: run it, read the `TypeError`, fix — do not ship the first answer because it looked right in chat. Layout now matches Mantine’s actual prop surface.

####Personal observation:

I distrust AI output on layout APIs about as much as I distrust it on skip logic in Week 3 — the diff looks confident until Python disagrees. Naming null findings in this file is part of the same habit: say what is empty instead of decorating around it.

## Connection to design / research practice

1. **Provenance first:** I wouldn’t quote a usability number without knowing which session file it came from; I shouldn’t quote a “citation” number without naming which `court_id` slice and whether `cite_count` is filled in there.

2. **Long labels are a UX problem:** Case titles are like long survey answers — the chart choice has to favor readability, not whatever the library defaults to.

3. **Flat metrics are still results:** If someone asks how cited King County appellate opinions are in this pull, the honest answer is “zero in this file’s `cite_count` column,” not a nicer chart that hides the gap.

## One thing I want to get better at next

1. Pin dependencies for Week 6 in a small `requirements-week6.txt` (or a lock file) so “install dash + dmc + kaleido” is one copy-paste for a grader, not only implied by my venv.

2. After `read_csv`, auto-build a one-page “data card” — shape, % missing judge, min/mean/max `cite_count` by `court_id` — and show it as a Mantine `Table` above the charts so caveats show up even if nobody opens this markdown.

—

## Notes / quotes / links

- Source table: `week 6/Week6_files/courtlistener_week5_repull_40k.csv`
- Interactive app: `week 6/courtlistener_mp1a_dash.py` (Dash + [Dash Mantine Components](https://www.dash-mantine-components.com/getting-started) + Plotly)
- Static submissions: `week 6/mp1a_chart1_court_level_cites_3d.jpg`, `week 6/mp1a_chart2_top_cited_cases_wd_wash.jpg`, `week 6/mp1a_chart3_top_authority_titles.jpg`
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
| `week6.md` | Competency mapping + chart reasons + null findings. |

—
