import os
import time
import hashlib
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

try:
    from googlesearch import search as google_search
except ImportError:
    raise ImportError("Install googlesearch-python: pip install googlesearch-python")

try:
    from newspaper import Article
except ImportError:
    raise ImportError("Install newspaper3k: pip install newspaper3k")

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

SKIP_DOMAINS = [
    "facebook.com", "twitter.com", "x.com", "linkedin.com",
    "instagram.com", "tiktok.com", "youtube.com", "reddit.com",
    "pinterest.com",
]

ACADEMIC_MARKERS = ["arxiv", "scholar.google", "ssrn", "acm.org", "ieee.org", "doi.org"]
NEWS_MARKERS = [
    "law.com", "reuters.com", "bloomberg.com", "nytimes.com",
    "abajournal.com", "legaltechnews", "lawsitesblog", "artificiallawyer",
    "techcrunch.com", "wired.com", "wsj.com",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def should_skip(url):
    return any(domain in url.lower() for domain in SKIP_DOMAINS)


def classify_source(url):
    url_lower = url.lower()
    if any(m in url_lower for m in ACADEMIC_MARKERS):
        return "academic"
    if any(m in url_lower for m in NEWS_MARKERS):
        return "news"
    return "blog"


def extract_domain(url):
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "")


def extract_with_newspaper(url):
    article = Article(url)
    article.download()
    article.parse()
    return {
        "title": article.title or "",
        "body_text": article.text or "",
        "author": ", ".join(article.authors) if article.authors else "",
        "published_date": article.publish_date.isoformat() if article.publish_date else "",
    }


def extract_with_bs4(url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    body_text = ""
    for tag_name in ["article", "main", "[role='main']"]:
        container = soup.find(tag_name)
        if container:
            body_text = container.get_text(separator=" ", strip=True)
            break
    if not body_text:
        body = soup.find("body")
        if body:
            for unwanted in body.find_all(["nav", "header", "footer", "script", "style", "aside"]):
                unwanted.decompose()
            body_text = body.get_text(separator=" ", strip=True)

    return {
        "title": title,
        "body_text": body_text[:5000],
        "author": "",
        "published_date": "",
    }


def collect_web():
    rows = []
    seen_urls = set()
    failed_urls = []

    for query in WEB_QUERIES:
        print(f"\nSearching Google: {query}")
        try:
            urls = list(google_search(query, num_results=10, lang="en"))
        except Exception as e:
            print(f"  Google search failed: {e}")
            time.sleep(5)
            continue

        for url in urls:
            if url in seen_urls or should_skip(url):
                continue
            seen_urls.add(url)

            print(f"  Scraping: {url[:80]}...")
            extracted = None

            try:
                extracted = extract_with_newspaper(url)
            except Exception:
                try:
                    extracted = extract_with_bs4(url)
                except Exception as e:
                    print(f"    Failed: {e}")
                    failed_urls.append(url)
                    continue

            if not extracted or len(extracted.get("body_text", "")) < 100:
                print(f"    Skipped (too short or empty)")
                failed_urls.append(url)
                continue

            row_id = hashlib.md5(url.encode()).hexdigest()[:12]
            rows.append({
                "id": row_id,
                "source": "web",
                "source_type": classify_source(url),
                "subreddit": "",
                "title": extracted["title"],
                "body_text": extracted["body_text"],
                "author": extracted["author"],
                "score": None,
                "num_comments": 0,
                "created_date": extracted["published_date"],
                "source_url": url,
                "post_type": "article",
                "parent_id": None,
                "domain": extract_domain(url),
            })
            time.sleep(1)

        time.sleep(2)

    os.makedirs("data", exist_ok=True)
    df_web = pd.DataFrame(rows)
    df_web.to_csv("data/raw_web.csv", index=False)

    print(f"\n=== Web Collection Complete ===")
    print(f"Articles scraped: {len(df_web)}")
    if len(df_web) > 0:
        print(f"By source type:")
        print(df_web["source_type"].value_counts().to_string())
    print(f"Failed URLs: {len(failed_urls)}")
    for u in failed_urls:
        print(f"  - {u[:80]}")

    merge_sources()


def merge_sources():
    reddit_path = "data/raw_reddit.csv"
    web_path = "data/raw_web.csv"

    frames = []
    if os.path.exists(reddit_path):
        df_reddit = pd.read_csv(reddit_path)
        frames.append(df_reddit)
        print(f"\nReddit rows: {len(df_reddit)}")
    else:
        print(f"\nWarning: {reddit_path} not found. Run 01_collect_reddit.py first.")

    if os.path.exists(web_path):
        df_web = pd.read_csv(web_path)
        if "domain" in df_web.columns:
            df_web = df_web.drop(columns=["domain"])
        frames.append(df_web)
        print(f"Web rows: {len(df_web)}")

    if not frames:
        print("No data to merge.")
        return

    unified_cols = [
        "id", "source", "source_type", "title", "body_text", "author",
        "score", "created_date", "source_url", "post_type",
    ]

    df_combined = pd.concat(frames, ignore_index=True)
    for col in unified_cols:
        if col not in df_combined.columns:
            df_combined[col] = ""

    df_combined.to_csv("data/raw_combined.csv", index=False)
    print(f"\nCombined rows: {len(df_combined)}")
    print(f"Saved to data/raw_combined.csv")


if __name__ == "__main__":
    collect_web()
