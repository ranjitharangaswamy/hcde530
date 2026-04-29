# Week 4 — Competency: Working with a live web API

```
#What I did this week

This week’s deliverable is a small Python script that talks to a real API over HTTPS, pulls structured JSON back, and extracts several fields into something a human can read. I deliberately did **not** reuse the class week-4 demo API (`hcde530-week4-api.onrender.com`) for the assignment piece — instead I used **CourtListener’s Citation Lookup and Verification API** ([docs](https://www.courtlistener.com/help/api/rest/citation-lookup/)): POST a blob of text (or volume/reporter/page), get back parsed citations plus match status and opinion clusters.

That choice is deliberate for my lane (law → HCDE): the response is explicitly designed as a **guardrail against hallucinated citations**, which is the same family of problem as “don’t trust summarized legal text without a pointer to authority.”

I kept the same habits as A2/A3: plain-English `#` comments on what the URL does, what the POST body is, what the JSON list means, and why each extracted field matters. I also mirror my week-3 instinct: print a readable slice **and** save `week4_citation_lookup_sample.json` so outputs are inspectable later.

```

## Competencies

### C — API request + response handling (Week 4 framing)

#### What the script is doing

`week4_public_api.py` sends **POST** `https://www.courtlistener.com/api/rest/v4/citation-lookup/` with `Content-Type: application/x-www-form-urlencoded` and form field `text=...`, per the [CourtListener citation-lookup docs](https://www.courtlistener.com/help/api/rest/citation-lookup/). Authentication is **`Authorization: Token <secret>`** (not Bearer). The token is read with **`os.environ.get("COURTLISTENER_API_TOKEN")`** after a tiny `.env` loader merges key/value lines into `os.environ` — no token is hardcoded, and `.env` stays out of git.

The API returns a **JSON list** (empty if no cites found); each element describes one detected citation: string form, character span in the input, `status` (200/300/404/400/429 semantics documented on their page), `error_message`, and `clusters` (matched opinions).

#### What I extract and why

I print more than the assignment minimum of three fields: **`citation`**, **`normalized_citations`** (canonicalization / ambiguity), **`status`**, **`error_message`**, **`start_index` / `end_index`**, plus **`case_name`** from the first cluster when present and the cluster count. Citation + status answer “what string did Eyecite find and did it resolve?”; indices answer “where would I highlight in the original paragraph?”; cluster case name gives a human-readable anchor for the first match.

#### personal observation

I still want a **written artifact** next to the console: the saved JSON is my audit trail, same energy as week 3’s CSV exports. For legal-tech APIs I also care about **status codes inside the JSON** (not just HTTP 200) because a 200 envelope can still carry a 404 “citation not found” payload per citation — the script surfaces both layers.

### Keys and `.env`

CourtListener **requires** a token. Pattern from the course brief: store `COURTLISTENER_API_TOKEN` in **`week 4/.env`**, never paste it into source, never commit it. Copy **`week 4/.env.example`** → `.env` and fill in the value. Repo `.gitignore` already ignores `.env`.

## Connection to design / research practice

1. **Guardrails for AI + research:** The docs frame citation lookup as helping prevent **hallucinated citations** — that is directly parallel to UX around “confidence + provenance” for any system that quotes authorities.
2. **Human-readable vs machine-complete:** I print a labeled summary but still save full JSON because `clusters` can be large; researchers often need both “at a glance” and “drill down.”
3. **Throttles and limits:** The same doc page notes per-minute caps, max citations per request, and max text length — any integration that ignores that will fail in the field the same way ignoring survey mess fails cleaning.

## One thing I want to get better at next

1. **CLI for arbitrary text:** Right now the sample string is fixed in `main()`; wiring `argparse` (or stdin) would make this a reusable desk tool for memos or participant quotes that mention cites.
2. **Volume/reporter/page mode:** The API also accepts `volume`, `reporter`, `page` form fields; a second code path would cover paste-from-shepard’s workflows without free-text parsing.

## Notes / quotes / links

- Citation Lookup API: https://www.courtlistener.com/help/api/rest/citation-lookup/
- Assignment script: `week 4/week4_public_api.py`
- Env template: `week 4/.env.example` → copy to `week 4/.env`
- Saved output (after a successful run): `week 4/week4_citation_lookup_sample.json`
- Class demo API (separate exercise): `week 4/API.py` → `https://hcde530-week4-api.onrender.com`

## Appendix — Week 4 artifacts

| Artifact | Role |
|----------|------|
| `week4_public_api.py` | POST citation-lookup, token from env, extract multiple fields, print + save JSON. |
| `.env.example` | Documents required env var name; no secrets. |
| `week4_citation_lookup_sample.json` | Written on successful run; holds API list for verification. |
| `API.py` | Earlier class work against the course Render API (reviews CSV). |
