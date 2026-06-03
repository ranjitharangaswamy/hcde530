import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

THEME_KEYWORDS = {
    "accuracy_trust": [
        "hallucinate", "hallucination", "wrong", "inaccurate", "trust",
        "reliable", "mistake", "error", "correct", "accuracy", "unreliable",
    ],
    "job_displacement": [
        "replace", "job", "automate", "unemploy", "displace", "obsolete",
        "hire", "layoff", "workforce", "career",
    ],
    "efficiency_gains": [
        "fast", "speed", "efficient", "productive", "save time", "workflow",
        "automate", "streamline", "hours", "minutes",
    ],
    "ethics_bias": [
        "bias", "ethical", "fairness", "discriminat", "justice", "equit",
        "transparent", "accountability",
    ],
    "cost_value": [
        "cost", "expensive", "cheap", "pricing", "worth", "afford",
        "bill", "fee", "subscription", "budget", "roi",
    ],
    "tool_review": [
        "harvey", "legora", "casetext", "lexis", "westlaw", "copilot",
        "chatgpt", "claude", "gemini", "clio", "litify",
    ],
    "regulation_compliance": [
        "regulat", "compli", "bar association", "unauthorized practice",
        "upl", "govern", "licensure", "oversight",
    ],
    "adoption_resistance": [
        "adopt", "resist", "refuse", "won't use", "skeptic", "luddite",
        "old school", "reluctan", "hesitan", "barrier",
    ],
}


def count_keyword_hits(text, keywords):
    return sum(1 for kw in keywords if kw in text)


def assign_keyword_themes(row):
    text = row["clean_text"]
    scores = {theme: count_keyword_hits(text, kws) for theme, kws in THEME_KEYWORDS.items()}
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    primary = ranked[0] if ranked[0][1] > 0 else (None, 0)
    secondary = ranked[1] if len(ranked) > 1 and ranked[1][1] >= 2 else (None, 0)

    return pd.Series({
        "primary_theme": primary[0],
        "primary_hits": primary[1],
        "secondary_theme": secondary[0],
    })


def cluster_uncoded(df_uncoded, n_clusters=5):
    if len(df_uncoded) < n_clusters:
        df_uncoded = df_uncoded.copy()
        df_uncoded["primary_theme"] = "uncategorized"
        df_uncoded["theme_confidence"] = "cluster"
        return df_uncoded

    vectorizer = TfidfVectorizer(max_features=500, stop_words="english")
    tfidf = vectorizer.fit_transform(df_uncoded["clean_text"])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(tfidf)

    feature_names = vectorizer.get_feature_names_out()
    cluster_labels = {}
    print("\n--- TF-IDF Cluster Centers (top terms) ---")
    for i in range(n_clusters):
        center = kmeans.cluster_centers_[i]
        top_indices = center.argsort()[-10:][::-1]
        top_terms = [feature_names[j] for j in top_indices]
        label = f"cluster_{i}_{'_'.join(top_terms[:3])}"
        cluster_labels[i] = label
        print(f"  Cluster {i}: {', '.join(top_terms)}")

    df_uncoded = df_uncoded.copy()
    df_uncoded["primary_theme"] = [cluster_labels[l] for l in labels]
    df_uncoded["theme_confidence"] = "cluster"
    return df_uncoded


def code_themes():
    df = pd.read_csv("data/cleaned_posts.csv")
    print(f"Loaded {len(df)} rows from cleaned_posts.csv")

    themes = df.apply(assign_keyword_themes, axis=1)
    df["primary_theme"] = themes["primary_theme"]
    df["primary_hits"] = themes["primary_hits"]
    df["secondary_theme"] = themes["secondary_theme"]

    coded = df[df["primary_theme"].notna()].copy()
    coded["theme_confidence"] = "keyword"
    uncoded = df[df["primary_theme"].isna()].copy()

    print(f"\nKeyword-coded: {len(coded)}")
    print(f"Uncoded (going to clustering): {len(uncoded)}")

    if len(uncoded) > 0:
        clustered = cluster_uncoded(uncoded)
        df_final = pd.concat([coded, clustered], ignore_index=True)
    else:
        df_final = coded

    df_final.to_csv("data/coded_posts.csv", index=False)

    print(f"\n=== Theme Coding Complete ===")
    print(f"Total coded rows: {len(df_final)}")
    print(f"\nTheme distribution:")
    print(df_final["primary_theme"].value_counts().to_string())
    print(f"\nSaved to data/coded_posts.csv")


if __name__ == "__main__":
    code_themes()
