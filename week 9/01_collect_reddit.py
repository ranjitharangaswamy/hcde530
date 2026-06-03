import os
import time
import sys
from datetime import datetime

try:
    import praw
    import pandas as pd
    from dotenv import load_dotenv
except ImportError as exc:
    print(
        f"Missing Python package: {exc.name}\n\n"
        "Install Week 9 dependencies with:\n"
        "python3 -m pip install -r 'week 9/requirements.txt'\n",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

SUBREDDITS = ["LawFirm", "lawyers", "LegalTech", "artificial", "ChatGPT"]
LEGAL_SUBS = ["LawFirm", "lawyers", "LegalTech"]

SEARCH_QUERIES = [
    "legal AI",
    "AI lawyer",
    "AI contract",
    "Harvey AI",
    "Legora",
    "AI legal research",
    "ChatGPT law",
    "AI deposition",
]

COMMENTS_PER_POST = 10

OUTPUT_COLUMNS = [
    "id",
    "source",
    "source_type",
    "subreddit",
    "title",
    "body_text",
    "author",
    "score",
    "num_comments",
    "created_date",
    "source_url",
    "post_type",
    "parent_id",
]


def validate_credentials():
    missing = [
        key for key in ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"]
        if not os.getenv(key)
    ]
    if missing:
        missing_list = ", ".join(missing)
        print(
            f"Missing Reddit API credentials: {missing_list}\n\n"
            "Create a free Reddit script app at:\n"
            "https://www.reddit.com/prefs/apps?screen_view_count=1\n\n"
            "Then create week 9/.env with:\n"
            "REDDIT_CLIENT_ID=your_client_id\n"
            "REDDIT_CLIENT_SECRET=your_client_secret\n"
            "REDDIT_USER_AGENT=hcde530_mp2a_research/1.0\n",
            file=sys.stderr,
        )
        raise SystemExit(1)


def init_reddit():
    validate_credentials()
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT", "hcde530_mp2a_research/1.0"),
    )


def submission_to_row(submission):
    return {
        "id": submission.id,
        "source": "reddit",
        "source_type": "post",
        "subreddit": submission.subreddit.display_name,
        "title": submission.title,
        "body_text": submission.selftext or "",
        "author": str(submission.author) if submission.author else "[deleted]",
        "score": submission.score,
        "num_comments": submission.num_comments,
        "created_date": datetime.utcfromtimestamp(submission.created_utc).isoformat(),
        "source_url": f"https://reddit.com{submission.permalink}",
        "post_type": "post",
        "parent_id": None,
    }


def comment_to_row(comment, subreddit_name):
    return {
        "id": comment.id,
        "source": "reddit",
        "source_type": "comment",
        "subreddit": subreddit_name,
        "title": "",
        "body_text": comment.body or "",
        "author": str(comment.author) if comment.author else "[deleted]",
        "score": comment.score,
        "num_comments": 0,
        "created_date": datetime.utcfromtimestamp(comment.created_utc).isoformat(),
        "source_url": f"https://reddit.com{comment.permalink}",
        "post_type": "comment",
        "parent_id": comment.parent_id,
    }


def collect():
    reddit = init_reddit()
    seen_ids = set()
    rows = []

    for sub_name in SUBREDDITS:
        subreddit = reddit.subreddit(sub_name)
        print(f"\n--- r/{sub_name} ---")

        for query in SEARCH_QUERIES:
            print(f"  Searching: {query}")
            try:
                for submission in subreddit.search(query, sort="relevance", time_filter="year", limit=100):
                    if submission.id in seen_ids:
                        continue
                    seen_ids.add(submission.id)
                    rows.append(submission_to_row(submission))

                    submission.comment_sort = "top"
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments[:COMMENTS_PER_POST]:
                        if comment.id not in seen_ids:
                            seen_ids.add(comment.id)
                            rows.append(comment_to_row(comment, sub_name))
            except Exception as e:
                print(f"    Error searching r/{sub_name} for '{query}': {e}")

            time.sleep(0.5)

        if sub_name in LEGAL_SUBS:
            print(f"  Fetching hot posts from r/{sub_name}")
            try:
                for submission in subreddit.hot(limit=200):
                    if submission.id in seen_ids:
                        continue
                    seen_ids.add(submission.id)
                    rows.append(submission_to_row(submission))

                    submission.comment_sort = "top"
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments[:COMMENTS_PER_POST]:
                        if comment.id not in seen_ids:
                            seen_ids.add(comment.id)
                            rows.append(comment_to_row(comment, sub_name))
            except Exception as e:
                print(f"    Error fetching hot from r/{sub_name}: {e}")

        time.sleep(0.5)

    df = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    os.makedirs(DATA_DIR, exist_ok=True)
    output_path = os.path.join(DATA_DIR, "raw_reddit.csv")
    df.to_csv(output_path, index=False)

    posts = df[df["post_type"] == "post"]
    comments = df[df["post_type"] == "comment"]
    print(f"\n=== Reddit Collection Complete ===")
    print(f"Total rows: {len(df)}")
    print(f"Posts: {len(posts)}, Comments: {len(comments)}")
    print(f"Posts per subreddit:")
    print(posts["subreddit"].value_counts().to_string() if len(posts) else "None")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    collect()
