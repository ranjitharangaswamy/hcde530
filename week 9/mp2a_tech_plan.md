# MP2a Tech Plan — Legal-AI Discourse Pipeline (Reddit + Web)

> Cursor handoff doc. Each phase is a self-contained task. Build them in order; each phase's outputs are the next phase's inputs.

---

## Project Structure

```
week 9/
├── mp2a_declaration_revised.md
├── mp2a_tech_plan.md          # this file
├── 01_collect_reddit.py       # Phase 1A: Reddit API ingestion
├── 01_collect_web.py          # Phase 1B: Google search + web scraping
├── 02_clean.py                # Phase 2: Text cleaning (both sources)
├── 03_code_themes.py          # Phase 3: Theme coding
├── 04_analyze.py              # Phase 4: Aggregation + memos
├── 05_qualitative.py          # Phase 5: Netnographic qualitative layer
├── mp2a_notebook.ipynb        # Phase 6: Analysis notebook (deliverable)
├── data/
│   ├── raw_reddit.csv         # output of Phase 1A
│   ├── raw_web.csv            # output of Phase 1B
│   ├── raw_combined.csv       # merged output of 1A + 1B
│   ├── cleaned_posts.csv      # output of Phase 2
│   ├── coded_posts.csv        # output of Phase 3
│   ├── themes_summary.csv     # output of Phase 4
│   ├── qualitative_coded.csv  # output of Phase 5 (enriched with sentiment/role/frame)
│   ├── community_norms.csv    # output of Phase 5 (reward/punish patterns)
│   ├── narratives.csv         # output of Phase 5 (first-person stories)
│   └── reflexive_memos.csv    # output of Phase 5 (interpretive memos)
└── .env                       # Reddit credentials (gitignored)
```

---

## Prerequisites

```bash
pip install praw pandas nltk scikit-learn python-dotenv jupyter requests beautifulsoup4 googlesearch-python newspaper3k
```

- **praw**: Reddit API wrapper (handles OAuth, pagination, rate limits)
- **nltk**: Tokenization, stopword removal
- **scikit-learn**: TF-IDF vectorization, optional clustering
- **python-dotenv**: Load `.env` credentials
- **requests + beautifulsoup4**: HTTP fetching and HTML parsing for web scraping
- **googlesearch-python**: Lightweight Google Search scraper (no API key needed)
- **newspaper3k**: Article text extraction from news/blog URLs (handles boilerplate removal)

### Reddit API Setup

1. Go to https://www.reddit.com/prefs/apps
2. Create a "script" type application
3. Note the `client_id`, `client_secret`, and set a `user_agent`
4. Create `week 9/.env`:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=hcde530_mp2a_research/1.0
```

---

## Phase 1A: Collect Reddit (`01_collect_reddit.py`)

**Goal:** Fetch public Reddit posts + comments about legal AI and save as `data/raw_reddit.csv`.

**Inputs:** Reddit API credentials, subreddit list
**Outputs:** `data/raw_reddit.csv` with columns: `id, source, subreddit, title, selftext, author, score, num_comments, created_utc, source_url, post_type`

> `source` = "reddit" for all rows. `source_url` = full permalink to the post or comment.

### Logic

1. Load credentials from `.env` using `python-dotenv`
2. Initialize PRAW Reddit instance
3. Define target subreddits: `["LawFirm", "lawyers", "LegalTech", "artificial", "ChatGPT"]`
4. Define search queries: `["legal AI", "AI lawyer", "AI contract", "Harvey AI", "Legora", "AI legal research", "ChatGPT law", "AI deposition"]`
5. For each subreddit, search with each query using `subreddit.search(query, sort="relevance", time_filter="year", limit=100)`
6. Also fetch top/hot posts from legal-specific subs (`LawFirm`, `lawyers`, `LegalTech`) with `limit=200`
7. Deduplicate by post `id`
8. For each post, also fetch top-level comments (limit 10 per post) — store as separate rows with `post_type="comment"` and a `parent_id` column
9. Save to `data/raw_reddit.csv`
10. Print summary: total posts, total comments, posts per subreddit

**Target:** 500–2000 rows total (posts + comments)

### Rate Limiting

PRAW handles rate limiting automatically. Add a `time.sleep(0.5)` between subreddit iterations as a courtesy buffer.

---

## Phase 1B: Collect Web (`01_collect_web.py`)

**Goal:** Scrape Google search results for legal-AI articles, news, and academic pages. Extract article text and save as `data/raw_web.csv`. Then merge with `data/raw_reddit.csv` into `data/raw_combined.csv`.

**Inputs:** Search queries (same topic as Reddit, broadened for web)
**Outputs:**
- `data/raw_web.csv` with columns: `id, source, source_type, title, body_text, author, published_date, source_url, domain`
- `data/raw_combined.csv` — unified schema merging Reddit + web rows

### Logic

1. Define search queries for Google:
   ```python
   WEB_QUERIES = [
       "legal AI adoption lawyers 2024",
       "AI litigation technology review",
       "Harvey AI legal tool review",
       "artificial intelligence law firm challenges",
       "legal tech AI accuracy concerns",
       "AI contract review lawyer experience",
       "legal AI ethics bias courtroom",
       "AI legal research tool comparison",
       "law firm AI adoption barriers",
       "legal AI regulation compliance 2024",
   ]
   ```

2. For each query, use `googlesearch-python` to get top 10 result URLs:
   ```python
   from googlesearch import search
   urls = list(search(query, num_results=10, lang="en"))
   ```

3. Filter out unwanted domains (social media, paywalled sites, PDFs):
   ```python
   SKIP_DOMAINS = ["facebook.com", "twitter.com", "x.com", "linkedin.com",
                    "instagram.com", "tiktok.com", "youtube.com", "reddit.com"]
   ```
   Skip `reddit.com` here since Reddit is covered by Phase 1A.

4. For each valid URL, extract article content using `newspaper3k`:
   ```python
   from newspaper import Article
   article = Article(url)
   article.download()
   article.parse()
   # article.title, article.text, article.authors, article.publish_date
   ```

5. If `newspaper3k` fails (some sites block it), fall back to `requests` + `BeautifulSoup`:
   ```python
   resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0 ..."}, timeout=10)
   soup = BeautifulSoup(resp.text, "html.parser")
   # Extract <article> or <main> tag text, fall back to <body>
   # Extract <title> tag
   ```

6. Classify `source_type` by domain pattern:
   - Domains containing "arxiv", "scholar", "ssrn", "acm", "ieee" → `"academic"`
   - Domains containing "law.com", "reuters", "bloomberg", "nytimes", "abajournal" → `"news"`
   - Everything else → `"blog"`

7. Generate a unique `id` per row (e.g., hash of URL)

8. Save to `data/raw_web.csv`

9. **Merge step:** Load `raw_reddit.csv` and `raw_web.csv`, normalize to a unified schema:
   ```
   id, source, source_type, title, body_text, author, score, created_date, source_url
   ```
   - Reddit rows: `source="reddit"`, `source_type="post"` or `"comment"`, `body_text` = selftext, `score` = upvote score, `created_date` = created_utc
   - Web rows: `source="web"`, `source_type` from step 6, `body_text` = article text, `score` = NaN (web has no upvotes), `created_date` = publish_date

10. Save merged dataframe to `data/raw_combined.csv`
11. Print summary: web articles fetched, articles per source_type, failed URLs, total combined rows

**Target:** 50–150 web articles + 500–2000 Reddit rows = 550–2150 combined rows

### Rate Limiting & Politeness

- Add `time.sleep(2)` between Google searches to avoid getting blocked
- Add `time.sleep(1)` between article downloads
- Set a proper `User-Agent` header
- Respect `robots.txt` — if a site blocks scraping, skip it and log the URL as failed
- Timeout requests after 10 seconds

### Safety

- Only scrape publicly accessible pages (no login walls, no paywalled content)
- Every row retains its `source_url` so the user can verify the original source
- No personal data is collected — only article titles, body text, author bylines, and publication dates from public pages

---

## Phase 2: Clean (`02_clean.py`)

**Goal:** Normalize and filter the raw text from both sources for analysis.

**Inputs:** `data/raw_combined.csv`
**Outputs:** `data/cleaned_posts.csv` — same schema plus `clean_text` column

### Logic

1. Load `raw_combined.csv`
2. Create `clean_text` from `body_text` column (already unified in merge step):
   - Lowercase
   - Remove URLs (regex: `https?://\S+`)
   - Remove Reddit markdown artifacts (`**`, `~~`, `>`, `#`)
   - Remove HTML tags that slipped through scraping (regex: `<[^>]+>`)
   - Remove special characters, keep alphanumeric + basic punctuation
   - Strip extra whitespace
3. For Reddit posts, prepend `title` to `clean_text` (title often contains the main topic)
4. Drop rows where `clean_text` is empty or < 20 characters
5. Drop exact duplicate `clean_text` values
6. Retain `source_url` on every row — this is the citation link
7. Save to `data/cleaned_posts.csv`
8. Print summary: rows before/after cleaning, drop rate, breakdown by source (reddit vs web)

---

## Phase 3: Code Themes (`03_code_themes.py`)

**Goal:** Assign each post/comment to one or more thematic codes using keyword-based coding + TF-IDF clustering.

**Inputs:** `data/cleaned_posts.csv`
**Outputs:** `data/coded_posts.csv` — adds columns: `primary_theme, secondary_theme, theme_confidence`

### Logic

#### Step A: Keyword-based initial codes

Define a dictionary of themes with associated keyword lists:

```python
THEME_KEYWORDS = {
    "accuracy_trust": ["hallucinate", "hallucination", "wrong", "inaccurate", "trust", "reliable", "mistake", "error", "correct"],
    "job_displacement": ["replace", "job", "automate", "unemploy", "displace", "obsolete", "hire", "layoff"],
    "efficiency_gains": ["fast", "speed", "efficient", "productive", "save time", "workflow", "automate", "streamline"],
    "ethics_bias": ["bias", "ethical", "fairness", "discriminat", "justice", "equit"],
    "cost_value": ["cost", "expensive", "cheap", "pricing", "worth", "afford", "bill", "fee", "subscription"],
    "tool_review": ["harvey", "legora", "casetext", "lexis", "westlaw", "copilot", "chatgpt", "claude", "gemini"],
    "regulation_compliance": ["regulat", "compli", "bar association", "unauthorized practice", "UPL", "govern"],
    "adoption_resistance": ["adopt", "resist", "refuse", "won't use", "skeptic", "luddite", "old school"],
}
```

For each row, scan `clean_text` for keyword matches. Assign `primary_theme` = theme with most keyword hits. Assign `secondary_theme` = second-most if >= 2 hits. Set `theme_confidence` = "keyword".

#### Step B: TF-IDF clustering for uncoded rows

1. Take rows where no keyword theme matched
2. Run TF-IDF vectorizer (max_features=500, stop_words="english")
3. Apply KMeans clustering (k=5)
4. Manually inspect cluster centers (top 10 terms per cluster) and assign a theme label to each cluster
5. Set `theme_confidence` = "cluster" for these rows

#### Step C: Save

Save full dataframe to `data/coded_posts.csv`.

---

## Phase 4: Analyze (`04_analyze.py`)

**Goal:** Aggregate themes into frequency-ranked summaries with illustrative excerpts and short memos.

**Inputs:** `data/coded_posts.csv`
**Outputs:** `data/themes_summary.csv`, printed memos to stdout (also saved as `data/memos.txt`)

### Logic

1. Load `coded_posts.csv`
2. Count `primary_theme` frequencies; rank descending
3. For each theme:
   - Count total posts + comments + articles
   - Calculate mean score (upvotes) for Reddit rows as a proxy for community agreement
   - Count by source: how many from Reddit vs web (shows cross-source validation)
   - Select top 3 illustrative excerpts (highest score for Reddit, longest match for web, clean_text truncated to 300 chars)
   - Include `source_url` for each excerpt so the user can click through to the original
   - Generate a one-paragraph thematic memo: "{theme} appeared in {n} items ({pct}% of corpus, {reddit_n} Reddit / {web_n} web). Practitioners primarily discuss {top keywords}. Representative excerpt: '{excerpt}' [source_url]. This theme suggests {brief interpretive note}."
4. Save `themes_summary.csv` with columns: `theme, count, percentage, reddit_count, web_count, mean_score, excerpt_1, excerpt_1_url, excerpt_2, excerpt_2_url, excerpt_3, excerpt_3_url, memo`
5. Save memos to `data/memos.txt`
6. Print ranked theme table to stdout

---

## Phase 5: Qualitative Netnographic Layer (`05_qualitative.py`)

**Goal:** Apply Kozinets-informed netnographic methods to enrich coded posts with sentiment, emotion, speaker roles, rhetorical framing, community norms, narrative extraction, and reflexive memos.

**Inputs:** `data/coded_posts.csv`
**Outputs:**
- `data/qualitative_coded.csv` — coded_posts + columns: `sentiment_compound, sentiment_label, dominant_emotion, speaker_role, rhetorical_frame`
- `data/community_norms.csv` — per-theme comparison of rewarded vs punished framing/sentiment
- `data/narratives.csv` — first-person experience stories with theme, role, emotion, excerpt, source_url
- `data/reflexive_memos.csv` + `data/reflexive_memos.txt` — interpretive memos per theme

### Logic

#### Step A: Sentiment & Emotion
- VADER `SentimentIntensityAnalyzer` → `sentiment_compound` (float) + `sentiment_label` (positive/negative/neutral)
- Emotion keyword lexicon (5 categories: frustration, enthusiasm, anxiety, skepticism, pragmatism) → `dominant_emotion`

#### Step B: Speaker Role Classification
- Regex patterns detect self-identification: practitioner ("I am a lawyer", "my firm"), law_student ("1L", "law school"), vendor_builder ("we built", "our product"), tech_adjacent ("software engineer"), client_public ("my lawyer", "not a lawyer")
- Unmatched → "unidentified"

#### Step C: Rhetorical Frame Detection
- Regex patterns classify how claims are positioned: lived_experience ("I tried", "in my experience"), fear_warning ("will destroy", "dangerous"), hype_promotion ("game changer", "disruptive"), measured_evaluation ("pros and cons", "it depends"), question_seeking ("has anyone tried"), authority_citation ("study shows", "according to")

#### Step D: Community Norms
- Split Reddit posts per theme by median score
- Compare emotion and framing distributions in high-score vs low-score halves
- Reveals what the community rewards (upvotes) vs punishes (downvotes)

#### Step E: Narrative Extraction
- Detect first-person experience markers ("I tried", "we implemented", "here's what happened")
- Pull top narratives per theme, ranked by score, with speaker role + emotion + source_url

#### Step F: Reflexive Memos
- Per-theme interpretive summary combining: sentiment distribution, dominant emotion, top rhetorical frame, speaker role breakdown, narrative count, community norm patterns
- Closer to netnographic fieldnotes than simple frequency reports

---

## Phase 6: Notebook (`mp2a_notebook.ipynb`)

**Goal:** Jupyter notebook that ties the pipeline together as the primary deliverable.

### Notebook Sections

1. **Introduction** — Research question
2. **Data Collection** — Run or import Phase 1A + 1B; show raw data shape, subreddit distribution, web source types breakdown
3. **Data Cleaning** — Run or import Phase 2; show before/after stats, source breakdown
4. **Theme Coding** — Run or import Phase 3; show theme distribution bar chart, cross-source stacked bar
5. **Analysis & Findings** — Run or import Phase 4; display ranked themes table, top excerpts per theme with clickable source links, memos
6. **Qualitative Netnographic Layer** — Run or import Phase 5; sentiment-by-theme stacked bars, speaker role + emotion side-by-side charts, community norms table, narrative excerpts with source links, reflexive memos
7. **Discussion** — Interpret top themes with netnographic insights; note limitations
8. **Future Work** — LinkedIn, longitudinal tracking, interactive Dash explorer, network analysis, comparative netnography

### Visualizations

- Bar chart: theme frequency
- Stacked bar: theme frequency by source (Reddit vs Web)
- Stacked bar: sentiment distribution by theme (red/gray/green)
- Side-by-side horizontal bars: speaker roles + dominant emotions
- Community norms table
- Narrative excerpts with role/emotion/source annotations

---

## `.gitignore` Additions

```
week 9/.env
week 9/data/
```

Keep CSV data out of git (can be large). The pipeline scripts regenerate everything.

---

## Build Order for Cursor

1. Create the directory structure and `.env` template
2. Build `01_collect_reddit.py` — test it, verify `data/raw_reddit.csv` has data
3. Build `01_collect_web.py` — test it, verify `data/raw_web.csv` has articles, verify `data/raw_combined.csv` merges both
4. Build `02_clean.py` — test it, verify `cleaned_posts.csv` looks right, check both reddit and web rows survive
5. Build `03_code_themes.py` — test it, inspect theme assignments manually
6. Build `04_analyze.py` — test it, read the memos for coherence, verify source_urls are present in excerpts
7. Build `05_qualitative.py` — test it, verify qualitative_coded.csv has sentiment/emotion/role/frame columns, check narratives.csv and reflexive_memos.txt
8. Build `mp2a_notebook.ipynb` — import all phase scripts, add markdown narrative, add all charts, verify source links render
9. Do a full end-to-end run: delete `data/`, run phases 1A → 1B → 2 → 3 → 4 → 5, open notebook, verify everything renders

---

## Key Decisions / Gotchas

- **PRAW, not raw HTTP.** PRAW handles OAuth, pagination, and rate limits. Don't roll your own Reddit API client.
- **Keyword coding first, clustering second.** The keyword dict gives interpretable, controllable codes. Clustering catches what keywords miss. This is defensible as a lightweight qualitative-quantitative hybrid — not claiming full grounded theory.
- **No LLM in the coding loop.** Keep it reproducible and transparent. An LLM-based coder is a valid extension but adds cost, latency, and a black box.
- **CSV, not SQLite.** For this scale (< 5k rows), CSV is simpler and the prof expects CSV deliverables.
- **Comments matter.** Reddit comments often contain more substantive practitioner opinions than the original posts. Fetch them.
