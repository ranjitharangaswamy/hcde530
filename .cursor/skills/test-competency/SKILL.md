---
name: test-competency
description: >-
  Verifies qualitative research responses against a user-research story framework,
  synthesizes a sample persona from the corpus, and produces a user journey map
  that centers stated needs. Use when the user asks to test competency against
  responses, validate interview quotes, verify survey narratives, run the test
  competency skill, or generate persona and journey outputs from collected data.
---

# Test competency (user research)

## When to use

Apply this skill when the project has **collected responses** (CSV, pasted quotes, or notes) and the goal is to:

1. **Verify** how well each response maps to credible **user research stories**
2. **Synthesize** one **sample persona** grounded in patterns across responses
3. **Map** a **user journey** that makes needs explicit across stages

Default data source for this repo: `week 2/demo_responses.csv` (columns `participant_id`, `role`, `response`). Adapt if the user points to another file or column names.

## Workflow

### 1. Load and scope

- Read the response set. Note N, roles if present, and any obvious themes.
- If the file is missing or `response` cells are empty, say so and stop with a short fix list.

### 2. Verify against user research stories

Use the verification system in [user-research-story-matrix.md](user-research-story-matrix.md).

For **each row** (or a representative sample if N is huge and the user only asked for a summary):

- Assign **story tags** (which narrative types appear).
- Rate **evidence strength**: strong / adequate / weak (see matrix).
- Note **gaps** (e.g., no outcome stated, only opinion, no context).

Produce a **verification summary**: counts by tag, share of strong vs weak evidence, and 2–4 bullets on what the corpus supports well vs what is underrepresented.

### 3. Sample persona

Build **one** persona named clearly as a **synthesis** (not a real individual):

- **Name + one-line snapshot** (role/context aligned with data).
- **Goals** (2–3) and **frustrations** (2–3) tied to recurring quotes or paraphrases.
- **Behaviors** and **constraints** inferred only from responses—flag anything speculative.
- **Quote anchors**: 2–4 short pull-quotes or paraphrases with participant IDs when available.

### 4. User journey map

Output a **markdown table** with at least these stages (merge or split if data demands):

| Stage | User actions / context | Needs (explicit) | Pain points | Opportunities |

- **Needs** must be written as needs (verbs: get, understand, avoid, complete…), not solutions.
- Every row should connect to at least one pattern from the verified responses.
- Add a closing **“Key moments”** list: 3–5 critical steps where needs peak.

### 5. Deliverables checklist

- [ ] Per-row or batched verification notes + aggregate verification summary
- [ ] One sample persona (labeled synthetic / based on corpus)
- [ ] Journey map table + key moments
- [ ] If writing to disk, use paths under `week 2/` unless the user specifies otherwise

## File output (optional)

If the user wants artifacts saved, prefer:

- `week 2/competency-verification.md` — verification tables and summary
- `week 2/sample-persona-and-journey.md` — persona + journey map

Do not overwrite `demo_responses.csv` or `context.md` unless the user asks.

## Additional reference

- Full story definitions and rubric: [user-research-story-matrix.md](user-research-story-matrix.md)
