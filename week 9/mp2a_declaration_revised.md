# MP2a Declaration (Revised v2)

## 1. Problem

Legal-tech researchers currently read Reddit and the open web by hand to find recurring complaints, adoption signals, and market evidence about legal AI tools. This project builds an automated pipeline that collects public discourse from Reddit (API) and general web sources (Google search scraping), then produces frequency-ranked themes with quoted evidence and verified source links, so researchers do not spend days manually reading and coding before a market or UX readout.

## 2. Audience

- **Primary:** Me, as a legal-tech and HCD researcher tracking how lawyers and practitioners talk about legal AI.
- **Secondary:** UX researchers and product managers at legal-tech companies (e.g., Harvey, Legora) who need frequency-ranked themes, illustrative quotes, and cited sources for positioning, roadmap, and competitive insight.

## 3. Data

- **Source A (primary):** Reddit API — public posts and comments from subreddits such as r/LawFirm, r/lawyers, r/LegalTech, r/artificial, r/ChatGPT filtered to legal-AI discussion.
- **Source B (supplementary):** Google search scraping — public articles from legal-tech blogs, news outlets, and academic/research pages. Each scraped item retains its source URL as a verified citation.
- **Storage:** Raw and processed rows stored as CSV. Every row carries a `source_url` for traceability.
- **Outputs:** A coded corpus with theme frequencies, illustrative excerpts sorted by frequency, short thematic memos, and clickable source links. The user queries a topic (e.g., "litigation legal tech") and gets back discussions, quotes, requirements, and stats with their original sources.

## 4. Track

Research track: collect, analyze, and synthesize. Primary deliverables are a Jupyter notebook, CSV datasets, and thematic insights. Visualization is optional and secondary.

## 5. Platform

Cursor + Python

## 6. Rationale

This project requires real computation: authenticating with the Reddit API, scraping Google search results, cleaning text from heterogeneous sources, coding excerpts into themes, and aggregating frequency-ranked outputs with source attribution. Cursor + Python supports a notebook-plus-CSV research pipeline, with an optional lightweight local UI later for theme exploration only.
