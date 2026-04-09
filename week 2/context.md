# Week 2 Context

## Project Goal
Build a small, beginner-friendly analysis workflow for qualitative UX research responses.
The project should support both:
- quick script-based exploration (`demo_word_count.py`)
- lightweight visual exploration (`dashboard.html`)

## Source of Truth
- Primary dataset: `demo_responses.csv`
- Columns expected: `participant_id`, `role`, `response`

If the CSV changes (more rows, updated text, new role distribution), outputs should update automatically without manual hardcoding.

## Dashboard Expectations
- Read data directly from `demo_responses.csv` at page load.
- Recompute summary metrics from current CSV contents.
- Show per-response details (participant, role, word count, preview).
- Show role-level totals to support quick comparison.

## Practical Notes
- Open `dashboard.html` through a local server so CSV fetch works reliably.
- Keep implementation dependency-free (plain HTML/CSS/JS).
- Prefer clear code over advanced patterns; this is coursework and should be easy to explain.

## Suggested Workflow
1. Update or replace rows in `demo_responses.csv`.
2. Run `python3 demo_word_count.py` for terminal summary.
3. Refresh `dashboard.html` to see updated visual summary.
