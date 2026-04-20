# Week 3 — Competency 3: Data cleaning & preparation

```
#What I did this week

This week had two parts: diagnosing and fixing a buggy analysis script, and extending a cleaning script to handle messy real-world survey data. 

###Did these tasks using Cursor and in-class code sessions
1. Built `clean_responses.py` to read messy survey CSVs, drop rows with empty names, coerce `experience_years` where possible, uppercase `role`, and write `clean_responses.csv` plus a plain-language `summarize_data` summary.
2. Reworked `week3_analysis_buggy.py`: fixed “top 5” satisfaction sorting, parsed numeric text (e.g. word years), skipped blank roles/names, added participant score details and `write_participant_scores_csv` to export `participant_scores_cleaned.csv`.
3. Added `count_roles.py` to group and print role frequencies from `responses.csv`.
4. Ran end-to-end flows from `week3_survey_messy.csv` through cleaning and scoring, checking terminal output and output files.

```
## Competencies 
###C3 — Data Cleaning and File Handling
####CrashBuggy
When I first ran week3_analysis_buggy.py on week3_survey_messy.csv, Python threw a ValueError on experience_years
<p>The error was on the int(row["experience_years"]) line in the average-experience block (around line 30). The script assumed experience_years would always be numeric text. 
Fixed this by replacing the bare int() call with a parser that handles both digit strings and number-words, and only includes a row's value in the average if it successfully parses. Rows with unparseable values are skipped, and the script reports how many were excluded.   
—
Personal observation: 
I like to notice which values were skipped and exactly why such skips were made, as I distrust AI communication regarding code decisions. So I made sure the output says explicitly what was skipped and why.  

####LogicBuggy
The results showed the wrong Top 5 results from the data. The original "Top 5 satisfaction scores" block sorted the rows ascending and took the first five. This showed the lowest five scores instead of the highest. 
<p> Fixed it by adding reverse=True before slicing, which checks the output against what was asked to the coding agent/ cursor agent.  

####Row issue
Blank role or name entries were leaking into summaries and the output CSV. I added skip logic in participant_score_details(row). If a row can't be scored (missing name, missing role, unparseable values), it returns None and gets filtered out before it reaches the output.

###C2
My two main commits for this week were:

1. "Bug 1 acquired. Numerical data in text format..." — marks when I identified and fixed the ValueError from experience_years = "fifteen" in clean_responses.py
2. "Added comments to clean_responses.py..." — in line comments

####personal observation: Clubbed multiple bug fixes in one commit, which does not explain the commit message accurately. I committed all fixes to errors in class, which was hard to track at the assignment reflection stage. This made me realize the importance of inline comments and clean code history for better clarity. 

## Connection to design / research practice

1. Survey exports from tools like Typeform or Qualtrics are rarely clean. I've assisted on research projects with 1000+ responses which took weeks to clean without AI or clean code. Its interesting to note that participants enter free text where numbers are expected, skip fields, or use inconsistent labels. Therefore, data cleaning is a prerequisite for any aggregate that's going to inform a persona or a design decision. 
2. A researcher who codes "frustrated" differently halfway through a dataset has the same problem as a script that handles "fifteen" differently from "15"
3. Exporting a cleaned CSV alongside the script creates an audit trail. Anyone who wants to verify the row counts or check dropped entries can do it without re-running the code. That matters in collaborative or client-facing research contexts where you're not the only person who needs to trust the numbers. 
—

## One thing I want to get better at next

1. I want to write better commit messages. It's tempting to use Cursor's auto messages, but my version of "bug acquired" gives a personalized touch, which is infact easier to remember for me. However, these messages might be unclear to third parties. I want to write messages that are self-contained enough that the diff is optional reading, not required.
2. The word-to-number parser is currently inline logic inside participant_score_details(). It should be its own named function with its own docstring, so that it can be reused and so the parent function stays readable. Centralizing shared helpers like this (parsing, role normalization) in one place would stop cleaning and analysis from drifting apart as the scripts evolve with time.  

—

## Notes / quotes / links

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


