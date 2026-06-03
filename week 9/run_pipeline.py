#!/usr/bin/env python3
"""
Litigation Legal Tech Pipeline — Web-scraping only (no Reddit API needed)
Uses Google search to find Reddit threads + legal-tech articles,
extracts text, codes themes, runs qualitative analysis, outputs results.
"""

import os
import sys
import time
import json
import hashlib
import re
from datetime import datetime
from urllib.parse import urlparse

import requests
import pandas as pd
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

import nltk
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Google queries scoped to Reddit
REDDIT_QUERIES = [
    "site:reddit.com litigation legal tech AI",
    "site:reddit.com AI tools for lawyers",
    "site:reddit.com legal AI ediscovery",
    "site:reddit.com AI deposition preparation lawyer",
    "site:reddit.com Harvey AI legal review",
    "site:reddit.com ChatGPT legal research attorney",
    "site:reddit.com AI contract review law firm",
    "site:reddit.com legal tech hallucination accuracy",
    "site:reddit.com AI replacing lawyers paralegal",
    "site:reddit.com best legal AI tools 2024",
    "site:reddit.com r/LegalTech AI",
    "site:reddit.com r/lawyers AI tools",
    "site:reddit.com r/LawFirm technology AI",
]

# Google queries for web articles
WEB_QUERIES = [
    "litigation legal technology AI 2024",
    "AI ediscovery tools review",
    "legal AI accuracy courtroom hallucination",
    "AI deposition preparation technology lawyer",
    "law firm AI adoption challenges litigation",
    "legal tech AI contract review experience",
    "Harvey AI legal review",
    "artificial intelligence litigation tool comparison",
]

SKIP_DOMAINS = [
    "facebook.com", "twitter.com", "x.com", "linkedin.com",
    "instagram.com", "tiktok.com", "youtube.com", "pinterest.com",
]

THEME_KEYWORDS = {
    "accuracy_trust": [
        "hallucinate", "hallucination", "wrong", "inaccurate", "trust",
        "reliable", "mistake", "error", "correct", "accuracy", "unreliable",
        "made up", "fabricat", "verified",
    ],
    "ediscovery_review": [
        "ediscovery", "e-discovery", "document review", "review platform",
        "relativity", "reveal", "nuix", "logikcull", "disco", "predictive coding",
        "tar", "technology assisted", "privilege review",
    ],
    "deposition_trial": [
        "deposition", "trial", "courtroom", "witness", "cross-examin",
        "testimony", "prep", "exhibit", "hearing", "motion",
    ],
    "efficiency_gains": [
        "fast", "speed", "efficient", "productive", "save time", "workflow",
        "automate", "streamline", "hours", "minutes", "billable",
    ],
    "job_displacement": [
        "replace", "job", "unemploy", "displace", "obsolete",
        "hire", "layoff", "workforce", "paralegal", "associate",
    ],
    "cost_value": [
        "cost", "expensive", "cheap", "pricing", "worth", "afford",
        "bill", "fee", "subscription", "budget", "roi", "value",
    ],
    "tool_review": [
        "harvey", "legora", "casetext", "lexis", "westlaw", "copilot",
        "chatgpt", "claude", "gemini", "clio", "litify", "vlex",
        "casemine", "fastcase", "ross",
    ],
    "ethics_regulation": [
        "regulat", "compli", "bar association", "unauthorized practice",
        "upl", "govern", "ethical", "bias", "fairness", "oversight",
        "malpractice", "duty", "competence",
    ],
    "adoption_resistance": [
        "adopt", "resist", "refuse", "skeptic", "luddite",
        "old school", "reluctan", "hesitan", "barrier", "won't use",
    ],
}

EMOTION_LEXICON = {
    "frustration": [
        "frustrat", "annoying", "annoyed", "ugh", "ridiculous", "useless",
        "waste of time", "broken", "terrible", "awful", "sucks", "disappointed",
    ],
    "enthusiasm": [
        "amazing", "love", "incredible", "game changer", "revolutionary",
        "excited", "blown away", "impressive", "fantastic", "awesome", "great",
    ],
    "anxiety": [
        "worried", "scary", "terrif", "concern", "afraid", "threat",
        "nervous", "uncertain", "alarming",
    ],
    "skepticism": [
        "doubt", "skeptic", "overhyp", "hype", "snake oil", "gimmick",
        "marketing", "buzzword", "vaporware", "not ready",
    ],
    "pragmatism": [
        "practical", "useful", "helpful", "works well", "saved me",
        "in practice", "workflow", "actually", "real world",
    ],
}

ROLE_PATTERNS = {
    "practitioner": [
        r"\bi am a lawyer\b", r"\bi'm a lawyer\b", r"\bi am an attorney\b",
        r"\bi'm an attorney\b", r"\bmy firm\b", r"\bmy practice\b",
        r"\bour firm\b", r"\bmy clients\b", r"\bat my firm\b",
        r"\bin my practice\b", r"\bi'm a paralegal\b",
    ],
    "law_student": [
        r"\blaw student\b", r"\b[123]l\b", r"\blaw school\b", r"\bbar exam\b",
    ],
    "vendor_builder": [
        r"\bwe built\b", r"\bour product\b", r"\bour tool\b",
        r"\bour platform\b", r"\bi'm building\b", r"\bco-?founder\b",
    ],
    "tech_adjacent": [
        r"\bi'm a developer\b", r"\bsoftware engineer\b", r"\bdata scientist\b",
    ],
}

FRAME_PATTERNS = {
    "lived_experience": [
        r"\bi (tried|used|tested)\b", r"\bin my experience\b",
        r"\bi've been using\b", r"\bwhen i used\b",
    ],
    "fear_warning": [
        r"\bthis (will|could) (destroy|kill|replace)\b",
        r"\bdangerous\b", r"\breckless\b",
    ],
    "hype_promotion": [
        r"\bgame changer\b", r"\bthe future of\b", r"\brevolution\b",
        r"\btransform(ing|ative)\b", r"\bdisrupt\b",
    ],
    "measured_evaluation": [
        r"\bpros and cons\b", r"\bon one hand\b", r"\bit depends\b",
        r"\bnuanc\b",
    ],
    "question_seeking": [
        r"\bhas anyone (tried|used)\b", r"\bwhat do you think\b",
        r"\brecommend\b", r"\bshould i\b",
    ],
}

NARRATIVE_MARKERS = [
    r"\bi (tried|used|tested|started|switched)\b",
    r"\bwe (implemented|adopted|rolled out|deployed)\b",
    r"\bafter (using|trying|testing)\b",
    r"\bmy experience with\b",
]


# ===================================================================
# Google Search
# ===================================================================

def google_search(query, num_results=10):
    """Search Google and return URLs."""
    try:
        from googlesearch import search as gsearch
        return list(gsearch(query, num_results=num_results, lang="en"))
    except Exception as e:
        print(f"    Google search failed: {e}")
        return []


# ===================================================================
# Reddit thread scraping via old.reddit.com
# ===================================================================

def scrape_reddit_thread(url):
    """Scrape a Reddit thread page for post + comments."""
    rows = []
    try:
        # Convert to old.reddit.com for simpler HTML
        clean_url = url.split("?")[0]
        if "old.reddit.com" not in clean_url:
            clean_url = clean_url.replace("www.reddit.com", "old.reddit.com")
            clean_url = clean_url.replace("reddit.com", "old.reddit.com")

        resp = requests.get(clean_url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return rows

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract subreddit
        sub_link = soup.find("a", class_="subreddit")
        subreddit = sub_link.get_text().replace("r/", "") if sub_link else ""

        # Extract post title
        title_el = soup.find("a", class_="title")
        title = title_el.get_text(strip=True) if title_el else ""

        # Extract post body
        post_body_el = soup.find("div", class_="usertext-body")
        post_body = post_body_el.get_text(separator=" ", strip=True) if post_body_el else ""

        # Extract post score
        score_el = soup.find("div", class_="score")
        score_text = score_el.get("title", "0") if score_el else "0"
        try:
            score = int(score_text)
        except (ValueError, TypeError):
            score = 0

        # Post row
        post_id = hashlib.md5(clean_url.encode()).hexdigest()[:12]
        rows.append({
            "id": post_id,
            "source": "reddit",
            "source_type": "post",
            "subreddit": subreddit,
            "title": title,
            "body_text": post_body,
            "author": "",
            "score": score,
            "num_comments": 0,
            "created_date": "",
            "source_url": url,
            "post_type": "post",
        })

        # Extract comments
        comment_divs = soup.find_all("div", class_="comment")
        for i, cdiv in enumerate(comment_divs[:15]):
            body_div = cdiv.find("div", class_="usertext-body")
            if not body_div:
                continue
            cbody = body_div.get_text(separator=" ", strip=True)
            if len(cbody) < 20:
                continue

            cscore_el = cdiv.find("span", class_="score")
            cscore = 0
            if cscore_el and cscore_el.get("title"):
                try:
                    cscore = int(cscore_el["title"])
                except (ValueError, TypeError):
                    pass

            cauthor_el = cdiv.find("a", class_="author")
            cauthor = cauthor_el.get_text(strip=True) if cauthor_el else ""

            rows.append({
                "id": f"{post_id}_c{i}",
                "source": "reddit",
                "source_type": "comment",
                "subreddit": subreddit,
                "title": "",
                "body_text": cbody,
                "author": cauthor,
                "score": cscore,
                "num_comments": 0,
                "created_date": "",
                "source_url": url,
                "post_type": "comment",
            })

    except Exception as e:
        print(f"      Thread scrape failed: {e}")

    return rows


def collect_reddit():
    print("\n" + "=" * 60)
    print("PHASE 1A: Finding & scraping Reddit threads via Google")
    print("=" * 60)

    all_rows = []
    seen_urls = set()

    for query in REDDIT_QUERIES:
        print(f"  Searching: {query}")
        urls = google_search(query, num_results=8)

        for url in urls:
            # Only process actual Reddit thread URLs
            if "reddit.com" not in url:
                continue
            # Skip non-thread pages
            if "/comments/" not in url:
                continue
            # Normalize
            base_url = url.split("?")[0]
            if base_url in seen_urls:
                continue
            seen_urls.add(base_url)

            print(f"    Scraping thread: {base_url[:70]}...")
            thread_rows = scrape_reddit_thread(base_url)
            all_rows.extend(thread_rows)
            time.sleep(1.5)

        time.sleep(2.5)

    df = pd.DataFrame(all_rows) if all_rows else pd.DataFrame()
    if len(df) > 0:
        df.to_csv(os.path.join(DATA_DIR, "raw_reddit.csv"), index=False)
        posts = df[df["post_type"] == "post"]
        comments = df[df["post_type"] == "comment"]
        print(f"\n  Reddit: {len(df)} rows ({len(posts)} posts, {len(comments)} comments)")
    else:
        print("\n  Reddit: 0 rows collected")
    return df


# ===================================================================
# PHASE 1B: Web articles
# ===================================================================

def scrape_article(url):
    """Extract article content from a URL."""
    try:
        from newspaper import Article
        art = Article(url)
        art.download()
        art.parse()
        return {
            "title": art.title or "",
            "body_text": art.text or "",
            "author": ", ".join(art.authors) if art.authors else "",
            "pub_date": art.publish_date.isoformat() if art.publish_date else "",
        }
    except Exception:
        pass

    # Fallback: requests + BS4
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("title").get_text(strip=True) if soup.find("title") else ""
        main = soup.find("article") or soup.find("main") or soup.find("body")
        if main:
            for tag in main.find_all(["nav", "header", "footer", "script", "style", "aside"]):
                tag.decompose()
            body = main.get_text(separator=" ", strip=True)[:5000]
        else:
            body = ""
        return {"title": title, "body_text": body, "author": "", "pub_date": ""}
    except Exception:
        return None


def collect_web():
    print("\n" + "=" * 60)
    print("PHASE 1B: Collecting web articles")
    print("=" * 60)

    ACADEMIC = ["arxiv", "scholar", "ssrn", "acm.org", "ieee.org"]
    NEWS = ["law.com", "reuters", "bloomberg", "nytimes", "abajournal",
            "artificiallawyer", "techcrunch", "legaltechnews"]

    rows = []
    seen = set()

    for q in WEB_QUERIES:
        print(f"  Google: '{q}'")
        urls = google_search(q, num_results=8)

        for url in urls:
            domain = urlparse(url).netloc.lower()
            if any(d in domain for d in SKIP_DOMAINS) or "reddit.com" in domain:
                continue
            if url in seen:
                continue
            seen.add(url)

            print(f"    Scraping: {url[:70]}...")
            extracted = scrape_article(url)
            if not extracted or len(extracted.get("body_text", "")) < 100:
                continue

            src_type = "academic" if any(m in url.lower() for m in ACADEMIC) else \
                       "news" if any(m in url.lower() for m in NEWS) else "blog"

            rows.append({
                "id": hashlib.md5(url.encode()).hexdigest()[:12],
                "source": "web",
                "source_type": src_type,
                "subreddit": "",
                "title": extracted["title"],
                "body_text": extracted["body_text"],
                "author": extracted["author"],
                "score": None,
                "num_comments": 0,
                "created_date": extracted["pub_date"],
                "source_url": url,
                "post_type": "article",
            })
            time.sleep(1.5)
        time.sleep(2.5)

    df = pd.DataFrame(rows) if rows else pd.DataFrame()
    if len(df) > 0:
        df.to_csv(os.path.join(DATA_DIR, "raw_web.csv"), index=False)
        print(f"\n  Web: {len(df)} articles")
    else:
        print("\n  Web: 0 articles collected")
    return df


# ===================================================================
# PHASE 2: Clean
# ===================================================================

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[*~>#]+", "", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    text = re.sub(r"[^a-z0-9\s.,!?'\"-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def run_clean(df_reddit, df_web):
    print("\n" + "=" * 60)
    print("PHASE 2: Cleaning text")
    print("=" * 60)

    frames = [f for f in [df_reddit, df_web] if len(f) > 0]
    if not frames:
        print("  No data to clean!")
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)
    df.to_csv(os.path.join(DATA_DIR, "raw_combined.csv"), index=False)

    df["body_text"] = df["body_text"].fillna("")
    df["title"] = df["title"].fillna("")

    reddit_posts = (df["source"] == "reddit") & (df["post_type"] == "post")
    df.loc[reddit_posts, "full_text"] = df.loc[reddit_posts, "title"] + " " + df.loc[reddit_posts, "body_text"]
    df.loc[~reddit_posts, "full_text"] = df.loc[~reddit_posts, "body_text"]
    df["clean_text"] = df["full_text"].apply(clean_text)

    before = len(df)
    df = df[df["clean_text"].str.len() >= 20]
    df = df.drop_duplicates(subset=["clean_text"])
    print(f"  {before} -> {len(df)} rows after cleaning")

    df.to_csv(os.path.join(DATA_DIR, "cleaned_posts.csv"), index=False)
    return df


# ===================================================================
# PHASE 3: Code themes
# ===================================================================

def run_code_themes(df):
    print("\n" + "=" * 60)
    print("PHASE 3: Coding themes")
    print("=" * 60)

    def assign(text):
        scores = {t: sum(1 for kw in kws if kw in text) for t, kws in THEME_KEYWORDS.items()}
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = ranked[0] if ranked[0][1] > 0 else (None, 0)
        secondary = ranked[1] if len(ranked) > 1 and ranked[1][1] >= 2 else (None, 0)
        return primary[0], secondary[0], primary[1]

    results = df["clean_text"].apply(lambda t: pd.Series(assign(t), index=["primary_theme", "secondary_theme", "primary_hits"]))
    df = pd.concat([df.reset_index(drop=True), results], axis=1)

    coded = df[df["primary_theme"].notna()].copy()
    coded["theme_confidence"] = "keyword"
    uncoded = df[df["primary_theme"].isna()].copy()

    if len(uncoded) > 5:
        vectorizer = TfidfVectorizer(max_features=300, stop_words="english")
        tfidf = vectorizer.fit_transform(uncoded["clean_text"])
        n_clusters = min(5, len(uncoded))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(tfidf)
        names = vectorizer.get_feature_names_out()
        cluster_map = {}
        for i in range(n_clusters):
            top = [names[j] for j in kmeans.cluster_centers_[i].argsort()[-3:][::-1]]
            cluster_map[i] = f"cluster_{'_'.join(top)}"
        uncoded["primary_theme"] = [cluster_map[l] for l in labels]
        uncoded["theme_confidence"] = "cluster"
        df_final = pd.concat([coded, uncoded], ignore_index=True)
    elif len(uncoded) > 0:
        uncoded["primary_theme"] = "uncategorized"
        uncoded["theme_confidence"] = "cluster"
        df_final = pd.concat([coded, uncoded], ignore_index=True)
    else:
        df_final = coded

    print(f"  Keyword-coded: {len(coded)}, Clustered: {len(uncoded)}")
    for t, c in df_final["primary_theme"].value_counts().head(10).items():
        print(f"    {t}: {c}")

    df_final.to_csv(os.path.join(DATA_DIR, "coded_posts.csv"), index=False)
    return df_final


# ===================================================================
# PHASE 4: Analyze
# ===================================================================

def run_analyze(df):
    print("\n" + "=" * 60)
    print("PHASE 4: Theme summaries")
    print("=" * 60)

    total = len(df)
    themes = df["primary_theme"].value_counts()
    summary = []

    for theme, count in themes.items():
        subset = df[df["primary_theme"] == theme]
        pct = round(count / total * 100, 1)
        reddit_n = len(subset[subset["source"] == "reddit"])
        web_n = len(subset[subset["source"] == "web"])

        reddit_sub = subset[subset["source"] == "reddit"]
        mean_score = round(pd.to_numeric(reddit_sub["score"], errors="coerce").mean(), 1) if len(reddit_sub) > 0 else 0

        excerpts = []
        for _, row in reddit_sub.nlargest(min(2, len(reddit_sub)), "score").iterrows():
            excerpts.append({"text": str(row["clean_text"])[:300], "url": row.get("source_url", "")})
        web_sub = subset[subset["source"] == "web"]
        for _, row in web_sub.head(1).iterrows():
            excerpts.append({"text": str(row["clean_text"])[:300], "url": row.get("source_url", "")})
        while len(excerpts) < 3:
            excerpts.append({"text": "", "url": ""})

        summary.append({
            "theme": theme, "count": count, "percentage": pct,
            "reddit_count": reddit_n, "web_count": web_n,
            "mean_score": mean_score,
            "excerpt_1": excerpts[0]["text"], "excerpt_1_url": excerpts[0]["url"],
            "excerpt_2": excerpts[1]["text"], "excerpt_2_url": excerpts[1]["url"],
            "excerpt_3": excerpts[2]["text"], "excerpt_3_url": excerpts[2]["url"],
        })

    df_sum = pd.DataFrame(summary)
    df_sum.to_csv(os.path.join(DATA_DIR, "themes_summary.csv"), index=False)
    print(f"  {len(df_sum)} themes summarized")
    return df_sum


# ===================================================================
# PHASE 5: Qualitative
# ===================================================================

def run_qualitative(df):
    print("\n" + "=" * 60)
    print("PHASE 5: Qualitative netnographic analysis")
    print("=" * 60)

    sia = SentimentIntensityAnalyzer()

    def get_sent(text):
        s = sia.polarity_scores(str(text))
        label = "positive" if s["compound"] >= 0.05 else ("negative" if s["compound"] <= -0.05 else "neutral")
        return s["compound"], label

    sent = df["clean_text"].apply(lambda t: pd.Series(get_sent(t), index=["sentiment_compound", "sentiment_label"]))
    df["sentiment_compound"] = sent["sentiment_compound"]
    df["sentiment_label"] = sent["sentiment_label"]

    def detect_emotion(text):
        text = str(text)
        hits = {e: sum(1 for kw in kws if kw in text) for e, kws in EMOTION_LEXICON.items()}
        hits = {k: v for k, v in hits.items() if v > 0}
        return max(hits, key=hits.get) if hits else "none"

    df["dominant_emotion"] = df["clean_text"].apply(detect_emotion)

    def classify_role(text):
        text = str(text)
        for role, patterns in ROLE_PATTERNS.items():
            if any(re.search(p, text) for p in patterns):
                return role
        return "unidentified"

    df["speaker_role"] = df["clean_text"].apply(classify_role)

    def classify_frame(text):
        text = str(text)
        hits = {f: sum(1 for p in pats if re.search(p, text)) for f, pats in FRAME_PATTERNS.items()}
        hits = {k: v for k, v in hits.items() if v > 0}
        return max(hits, key=hits.get) if hits else "unframed"

    df["rhetorical_frame"] = df["clean_text"].apply(classify_frame)

    df["is_narrative"] = df["clean_text"].apply(
        lambda t: any(re.search(p, str(t)) for p in NARRATIVE_MARKERS)
    )

    df.to_csv(os.path.join(DATA_DIR, "qualitative_coded.csv"), index=False)

    # Narratives
    narr_rows = []
    for theme in df["primary_theme"].dropna().unique():
        subset = df[(df["primary_theme"] == theme) & (df["is_narrative"])]
        subset = subset.copy()
        subset["score"] = pd.to_numeric(subset["score"], errors="coerce").fillna(0)
        for _, row in subset.nlargest(min(3, len(subset)), "score").iterrows():
            narr_rows.append({
                "theme": theme, "speaker_role": row["speaker_role"],
                "sentiment": row["sentiment_label"], "emotion": row["dominant_emotion"],
                "excerpt": str(row["clean_text"])[:500],
                "source_url": row.get("source_url", ""), "source": row["source"],
            })
    df_narr = pd.DataFrame(narr_rows)
    df_narr.to_csv(os.path.join(DATA_DIR, "narratives.csv"), index=False)

    # Community norms
    reddit = df[df["source"] == "reddit"].copy()
    reddit["score"] = pd.to_numeric(reddit["score"], errors="coerce")
    norms = []
    for theme in reddit["primary_theme"].dropna().unique():
        sub = reddit[reddit["primary_theme"] == theme]
        if len(sub) < 4:
            continue
        med = sub["score"].median()
        hi = sub[sub["score"] > med]
        lo = sub[sub["score"] <= med]
        norms.append({
            "theme": theme, "median_score": med,
            "rewarded_frames": str(hi["rhetorical_frame"].value_counts().head(2).to_dict()),
            "punished_frames": str(lo["rhetorical_frame"].value_counts().head(2).to_dict()),
            "rewarded_sentiment_avg": round(hi["sentiment_compound"].mean(), 3) if len(hi) else 0,
            "punished_sentiment_avg": round(lo["sentiment_compound"].mean(), 3) if len(lo) else 0,
        })
    pd.DataFrame(norms).to_csv(os.path.join(DATA_DIR, "community_norms.csv"), index=False)

    # Reflexive memos
    memos = []
    for theme in df["primary_theme"].dropna().unique():
        sub = df[df["primary_theme"] == theme]
        n = len(sub)
        if n < 3:
            continue
        reddit_n = len(sub[sub["source"] == "reddit"])
        web_n = len(sub[sub["source"] == "web"])
        sdist = sub["sentiment_label"].value_counts(normalize=True)
        pos = round(sdist.get("positive", 0) * 100)
        neg = round(sdist.get("negative", 0) * 100)
        neu = round(sdist.get("neutral", 0) * 100)
        top_emo = sub["dominant_emotion"].value_counts().index[0]
        top_frame = sub["rhetorical_frame"].value_counts().index[0]
        roles = sub["speaker_role"].value_counts().head(3).to_dict()
        role_str = ", ".join(f"{r} ({c})" for r, c in roles.items())
        narr_count = int(sub["is_narrative"].sum())

        memo = (
            f"{theme}: {n} items ({reddit_n} Reddit, {web_n} web). "
            f"Emotion: {top_emo}. Sentiment: {pos}% pos / {neg}% neg / {neu}% neutral. "
            f"Frame: {top_frame}. Roles: {role_str}. Narratives: {narr_count}."
        )
        memos.append({"theme": theme, "memo": memo})

    pd.DataFrame(memos).to_csv(os.path.join(DATA_DIR, "reflexive_memos.csv"), index=False)

    print(f"  Sentiment: {df['sentiment_label'].value_counts().to_dict()}")
    print(f"  Emotions: {df['dominant_emotion'].value_counts().head(5).to_dict()}")
    print(f"  Roles: {df['speaker_role'].value_counts().to_dict()}")
    print(f"  Narratives: {len(df_narr)}")
    print(f"  Memos: {len(memos)}")

    return df


# ===================================================================
# Main
# ===================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LITIGATION LEGAL TECH DISCOURSE PIPELINE")
    print("=" * 60)

    df_reddit = collect_reddit()
    df_web = collect_web()
    df_clean = run_clean(df_reddit, df_web)

    if len(df_clean) == 0:
        print("\nNo data collected. Exiting.")
        sys.exit(1)

    df_coded = run_code_themes(df_clean)
    df_summary = run_analyze(df_coded)
    df_qual = run_qualitative(df_coded)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"  Total items: {len(df_qual)}")
    print(f"  Themes: {df_qual['primary_theme'].nunique()}")
    print(f"  Output files in: {DATA_DIR}/")
    print(f"\n  Run: python3 app.py   to launch the UI")
