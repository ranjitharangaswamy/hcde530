# Week 4 — APIs and Data Acquisition

```
#What I did this week
1. This week I wrote a Python script that authenticates against a live web API, makes a real HTTP request, and parses the structured JSON response into something readable. 
2. I deliberately did not use the class demo API (hcde530-week4-api.onrender.com) for the assignment. I used CourtListener via its official Python client (courtlistener-api-client), which wraps the v4 REST endpoints. (I had to google the types of APIs available on their site and use github instructions to find my key, which was ironic!)
3. The default script calls citation lookup (client.citation_lookup.lookup_text(...)). An optional --examples flag runs the opinions and dockets patterns, including paginated results.

#What does this API do? (for non-legal folks)
CourtListener's citation lookup is explicitly designed as a guardrail against hallucinated legal citations. It checks whether a cited case actually exists and resolves to a real opinion. That is the same category of problem as verifying a source before acting on it, which is a judgment I apply every time I read a contract or a brief.

###Did these tasks using Cursor and Python
1. Built week4_public_api.py to authenticate with a token stored in .env, call the CourtListener citation lookup endpoint, parse the JSON list response, and print a labeled summary to console.
2. Saved full JSON output to week4_citation_lookup_sample.json as an audit trail alongside the printed summary.
3. Read the rate-limit docs before writing — per-minute caps, max citations per request, max text length.
4. Added .env.example as a template so the required variable name is documented without any secret in the repo.

```
## Competencies 
###C4 — APIs and data acquisition
# Week 4 — Competency 4: Working with a live web API

```

#### The endpoint and what comes back

The script calls POST /citation-lookup/ via client.citation_lookup.lookup_text(...). It takes a block of text, runs it through CourtListener's citation extractor, and returns a JSON list — one element per detected citation. Each element includes: citation (the raw string), normalized_citations (canonical form), status (per-citation code: 200, 404, 429 etc.), error_message, start_index / end_index (character offsets), and clusters (matched opinions with case_name).

<p>The choice of API was deliberate for my background (law + HCDE): citation lookup is explicitly framed as a guardrail against hallucinated citations — checking whether a cited case actually exists and resolves to a real opinion. That's a problem I care about. I don't have to quote an authoritative citation that I haven't verified.

####Personal observation:
I extract all fields, not just the three-field minimum. A 200 HTTP response can still carry a 404 per-citation payload — the citation was detected but matched nothing. Surfacing both layers is the difference between knowing the API call ran and knowing the result is usable. I distrust output that only shows me the top level.

#### Output

I print a labeled console summary (citation, status, case_name from first cluster) and save the full JSON to week4_citation_lookup_sample.json. The summary answers "did this cite resolve and to what?" The saved JSON is the drill-down record when clusters are large. 
```

## Connection to design / research practice

1. Citation lookup is a provenance checker. Any system that quotes authority — a research summary, compliance checklist, AI-generated brief — needs something that answers "does this source actually exist?" I've seen this fail in practice when summarized legal text gets passed around without a pointer back to the original.
2. I print a quick summary but keep the full JSON because researchers need both orientations: the at-a-glance read and the ability to go deeper. Designing for one without the other is a gap.
3. I read the rate-limit documentation before writing. Caps and length limits exist for a reason. Ignoring them fails the same way ignoring messy data fails — silently, and too late to fix cleanly. I had to read quite a bit on the CourtListener website to understand the free tier usage.

```

## One thing I want to get better at next

1. The citation text is hardcoded in main() right now. How do I build a version where I paste any paragraph from a memo or research note and get verification back immediately? That's the version I'd actually use.
2. The API also accepts volume, reporter, and page as discrete fields instead of free text. A second input path would cover cases where you already have a structured cite and just need to confirm it resolves. That's closer to how legal professionals actually encounter citations.

—


