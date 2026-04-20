# Week 3 — Competency 5: Data cleaning & preparation

```
## What Competency 5 means to me

**Data cleaning and preparation (my working definition):** Data cleaning is the work of turning messy, inconsistent inputs into a dataset you can trust—fixing missing values, normalizing labels, parsing numbers that appear as text, and documenting what you dropped or changed so analysis is reproducible. This week I claim **C5: Data Cleaning and Preparation** because I wrote scripts that filter invalid rows, standardize roles, convert experience fields to usable numbers, and export cleaned tables for downstream use. That work connects directly to responsible analysis: garbage in still means garbage out, but deliberate cleaning narrows the gap between raw responses and defensible summaries.

```

## What I did this week

1. Built `clean_responses.py` to read messy survey CSVs, drop rows with empty names, coerce `experience_years` where possible, uppercase `role`, and write `clean_responses.csv` plus a plain-language `summarize_data` summary.
2. Reworked `week3_analysis_buggy.py`: fixed “top 5” satisfaction sorting, parsed numeric text (e.g. word years), skipped blank roles/names, added participant score details and `write_participant_scores_csv` to export `participant_scores_cleaned.csv`.
3. Added `count_roles.py` to group and print role frequencies from `responses.csv`.
4. Ran end-to-end flows from `week3_survey_messy.csv` through cleaning and scoring, checking terminal output and output files.

—

## Observations — data cleaning

Cleaning felt less like “fixing typos” and more like **making explicit rules**: what counts as missing, what to exclude, and how to treat edge cases (e.g. non-numeric experience). The messy file made it obvious that **schema assumptions break silently**—column names like `participant_name` vs `name` changed whether rows looked “empty.”

A growth area is standardizing one pipeline (read → validate → transform → write) so every script shares the same definitions of “clean.”

—

## Observations — documentation & traceability

Small outputs (`clean_responses.csv`, `participant_scores_cleaned.csv`) act as **checkpoints**: they show what survived filtering and what was computed. Pairing those files with short printed summaries makes it easier to explain results to someone who did not run the code.

What was challenging was choosing whether to drop bad rows or flag them—dropping is simpler but can hide how much data was lost.

—

## Connection to design / research practice

1. Survey and interview exports are often inconsistent; cleaning is a prerequisite for fair aggregates and personas.
2. Role normalization and numeric parsing mirror qualitative coding choices: categories must be stable enough to compare across rows.
3. Exporting cleaned CSVs supports collaboration and audit—others can verify counts without re-running every step.

—

## One thing I want to get better at next

1. Centralize shared helpers (parse, role normalization) in one module so cleaning and analysis never drift apart.
2. Add lightweight validation reports (counts before/after, dropped-row reasons) next to every cleaned file.

—

## Notes / quotes / links

*(Optional: syllabus lines, feedback, or resources.)*

- Source data: `week3_survey_messy.csv`
- Cleaned outputs: `clean_responses.csv`, `participant_scores_cleaned.csv`

—

## Data appendix — Week 3 artifacts

| Artifact | Role |
|----------|------|
| `week3_survey_messy.csv` | Raw input (inconsistent casing, missing names, text numerals). |
| `clean_responses.py` / `clean_responses.csv` | Rule-based cleaning and summarized row/role/name stats via `summarize_data`. |
| `week3_analysis_buggy.py` | Analysis, top-N satisfaction, participant score + CSV export. |
| `count_roles.py` | Role frequency counts from `responses.csv`. |

*Regenerate or extend this section if filenames or pipelines change.*
