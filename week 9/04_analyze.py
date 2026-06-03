import pandas as pd


def analyze():
    df = pd.read_csv("data/coded_posts.csv")
    print(f"Loaded {len(df)} coded rows")

    total = len(df)
    themes = df["primary_theme"].value_counts()

    summary_rows = []

    for theme, count in themes.items():
        subset = df[df["primary_theme"] == theme]
        pct = round(count / total * 100, 1)

        reddit_count = len(subset[subset["source"] == "reddit"])
        web_count = len(subset[subset["source"] == "web"])

        reddit_subset = subset[subset["source"] == "reddit"]
        mean_score = round(reddit_subset["score"].mean(), 1) if len(reddit_subset) > 0 else 0

        excerpts = []
        reddit_top = reddit_subset.nlargest(2, "score") if "score" in reddit_subset.columns else reddit_subset.head(2)
        for _, row in reddit_top.iterrows():
            text = str(row["clean_text"])[:300]
            url = row.get("source_url", "")
            excerpts.append((text, url))

        web_subset = subset[subset["source"] == "web"]
        web_top = web_subset.head(1)
        for _, row in web_top.iterrows():
            text = str(row["clean_text"])[:300]
            url = row.get("source_url", "")
            excerpts.append((text, url))

        while len(excerpts) < 3:
            remaining = subset[~subset.index.isin(
                reddit_top.index.tolist() + web_top.index.tolist()
            )].head(1)
            for _, row in remaining.iterrows():
                excerpts.append((str(row["clean_text"])[:300], row.get("source_url", "")))
            if remaining.empty:
                excerpts.append(("", ""))

        memo = (
            f"{theme} appeared in {count} items ({pct}% of corpus, "
            f"{reddit_count} Reddit / {web_count} web). "
            f"Representative excerpt: '{excerpts[0][0][:150]}...' [{excerpts[0][1]}]."
        )

        summary_rows.append({
            "theme": theme,
            "count": count,
            "percentage": pct,
            "reddit_count": reddit_count,
            "web_count": web_count,
            "mean_score": mean_score,
            "excerpt_1": excerpts[0][0] if len(excerpts) > 0 else "",
            "excerpt_1_url": excerpts[0][1] if len(excerpts) > 0 else "",
            "excerpt_2": excerpts[1][0] if len(excerpts) > 1 else "",
            "excerpt_2_url": excerpts[1][1] if len(excerpts) > 1 else "",
            "excerpt_3": excerpts[2][0] if len(excerpts) > 2 else "",
            "excerpt_3_url": excerpts[2][1] if len(excerpts) > 2 else "",
            "memo": memo,
        })

    df_summary = pd.DataFrame(summary_rows)
    df_summary.to_csv("data/themes_summary.csv", index=False)

    memos_text = []
    print(f"\n{'='*60}")
    print(f"THEME ANALYSIS — {total} items across Reddit + Web")
    print(f"{'='*60}")

    for _, row in df_summary.iterrows():
        block = (
            f"\n## {row['theme']} ({row['count']} items, {row['percentage']}%)\n"
            f"Reddit: {row['reddit_count']} | Web: {row['web_count']} | "
            f"Mean Reddit Score: {row['mean_score']}\n\n"
            f"Excerpt 1: \"{row['excerpt_1']}\"\n"
            f"  Source: {row['excerpt_1_url']}\n\n"
            f"Excerpt 2: \"{row['excerpt_2']}\"\n"
            f"  Source: {row['excerpt_2_url']}\n\n"
            f"Excerpt 3: \"{row['excerpt_3']}\"\n"
            f"  Source: {row['excerpt_3_url']}\n\n"
            f"Memo: {row['memo']}\n"
        )
        print(block)
        memos_text.append(block)

    with open("data/memos.txt", "w") as f:
        f.write(f"THEME ANALYSIS — {total} items across Reddit + Web\n")
        f.write("=" * 60 + "\n")
        f.writelines(memos_text)

    print(f"\nSaved data/themes_summary.csv")
    print(f"Saved data/memos.txt")


if __name__ == "__main__":
    analyze()
