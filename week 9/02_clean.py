import re
import pandas as pd


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


def clean():
    df = pd.read_csv("data/raw_combined.csv")
    print(f"Loaded {len(df)} rows from raw_combined.csv")
    print(f"  Reddit: {len(df[df['source'] == 'reddit'])}")
    print(f"  Web:    {len(df[df['source'] == 'web'])}")

    df["body_text"] = df["body_text"].fillna("")
    df["title"] = df["title"].fillna("")

    reddit_posts = (df["source"] == "reddit") & (df["post_type"] == "post")
    df.loc[reddit_posts, "full_text"] = df.loc[reddit_posts, "title"] + " " + df.loc[reddit_posts, "body_text"]
    df.loc[~reddit_posts, "full_text"] = df.loc[~reddit_posts, "body_text"]

    df["clean_text"] = df["full_text"].apply(clean_text)

    before = len(df)
    df = df[df["clean_text"].str.len() >= 20]
    short_dropped = before - len(df)

    before2 = len(df)
    df = df.drop_duplicates(subset=["clean_text"])
    dup_dropped = before2 - len(df)

    df.to_csv("data/cleaned_posts.csv", index=False)

    print(f"\n=== Cleaning Complete ===")
    print(f"Rows after cleaning: {len(df)}")
    print(f"  Dropped (too short): {short_dropped}")
    print(f"  Dropped (duplicates): {dup_dropped}")
    print(f"  Reddit: {len(df[df['source'] == 'reddit'])}")
    print(f"  Web:    {len(df[df['source'] == 'web'])}")
    print(f"Saved to data/cleaned_posts.csv")


if __name__ == "__main__":
    clean()
