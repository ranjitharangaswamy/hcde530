"""
Phase 5: Qualitative Netnographic Analysis Layer

Goes beyond theme frequency to capture the cultural and experiential
dimensions of legal-AI discourse using Kozinets-informed netnographic
methods adapted for computational analysis:

1. Sentiment & Emotion — VADER polarity + emotion keyword tagging
2. Speaker Role — classify who is talking (practitioner, student, vendor, etc.)
3. Rhetorical Frame — how they position their claims (experience, fear, hype, etc.)
4. Community Norms — detect what the community rewards/punishes via score patterns
5. Narrative Extraction — pull first-person experience stories
6. Reflexive Memos — interpretive summaries per theme combining all layers
"""

import pandas as pd
import re
from collections import Counter

try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    import nltk
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except LookupError:
        nltk.download("vader_lexicon", quiet=True)
except ImportError:
    raise ImportError("Install nltk: pip install nltk")


# ---------------------------------------------------------------------------
# 1. Sentiment & Emotion
# ---------------------------------------------------------------------------

EMOTION_LEXICON = {
    "frustration": [
        "frustrat", "annoying", "annoyed", "ugh", "ridiculous", "useless",
        "waste of time", "broken", "terrible", "awful", "horrible", "sucks",
        "disappointed", "infuriat",
    ],
    "enthusiasm": [
        "amazing", "love", "incredible", "game changer", "revolutionary",
        "excited", "blown away", "impressive", "fantastic", "awesome",
        "powerful", "great",
    ],
    "anxiety": [
        "worried", "scary", "terrif", "concern", "afraid", "threat",
        "nervous", "uncertain", "unsettl", "alarming", "dystop",
    ],
    "skepticism": [
        "doubt", "skeptic", "overhyp", "hype", "snake oil", "gimmick",
        "marketing", "buzzword", "vaporware", "not ready", "premature",
    ],
    "pragmatism": [
        "practical", "useful", "helpful", "works well", "saved me",
        "in practice", "day to day", "workflow", "actually", "real world",
    ],
}


def get_sentiment(text, analyzer):
    scores = analyzer.polarity_scores(text)
    if scores["compound"] >= 0.05:
        label = "positive"
    elif scores["compound"] <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return pd.Series({
        "sentiment_compound": round(scores["compound"], 3),
        "sentiment_label": label,
    })


def detect_emotions(text):
    hits = {}
    for emotion, keywords in EMOTION_LEXICON.items():
        count = sum(1 for kw in keywords if kw in text)
        if count > 0:
            hits[emotion] = count
    if not hits:
        return "none"
    ranked = sorted(hits.items(), key=lambda x: x[1], reverse=True)
    return ranked[0][0]


# ---------------------------------------------------------------------------
# 2. Speaker Role Classification
# ---------------------------------------------------------------------------

ROLE_PATTERNS = {
    "practitioner": [
        r"\bi am a lawyer\b", r"\bi'm a lawyer\b", r"\bi am an attorney\b",
        r"\bi'm an attorney\b", r"\bmy firm\b", r"\bmy practice\b",
        r"\bour firm\b", r"\bmy clients\b", r"\byears of practice\b",
        r"\bpracticing for\b", r"\bat my firm\b", r"\bmy associates\b",
        r"\bin my practice\b", r"\bi'm a paralegal\b", r"\bi am a paralegal\b",
    ],
    "law_student": [
        r"\blaw student\b", r"\b1l\b", r"\b2l\b", r"\b3l\b",
        r"\blaw school\b", r"\bbar exam\b", r"\bjuris doctor\b",
        r"\bjd student\b", r"\bpassing the bar\b",
    ],
    "vendor_builder": [
        r"\bwe built\b", r"\bour product\b", r"\bour tool\b",
        r"\bour platform\b", r"\bi'm building\b", r"\bi built\b",
        r"\bco-?founder\b", r"\bour startup\b", r"\bwe launched\b",
        r"\bcheck out my\b", r"\bfull disclosure\b",
    ],
    "tech_adjacent": [
        r"\bi'm a developer\b", r"\bi'm an engineer\b", r"\bsoftware engineer\b",
        r"\bdata scientist\b", r"\bml engineer\b", r"\bi work in tech\b",
        r"\btech background\b",
    ],
    "client_public": [
        r"\bmy lawyer\b", r"\bmy attorney\b", r"\bhired a lawyer\b",
        r"\bas a client\b", r"\bnot a lawyer\b", r"\bnal\b",
        r"\bi needed legal\b",
    ],
}


def classify_role(text):
    for role, patterns in ROLE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return role
    return "unidentified"


# ---------------------------------------------------------------------------
# 3. Rhetorical Frame Detection
# ---------------------------------------------------------------------------

FRAME_PATTERNS = {
    "lived_experience": [
        r"\bi (tried|used|tested|experimented)\b",
        r"\bin my experience\b", r"\bfrom my experience\b",
        r"\bi've been using\b", r"\bwhen i used\b",
        r"\bi (personally|actually) (use|used|tried)\b",
    ],
    "fear_warning": [
        r"\bthis (will|could|is going to) (destroy|kill|end|replace)\b",
        r"\bmark my words\b", r"\bslippery slope\b", r"\bwatch out\b",
        r"\bdangerous\b", r"\breckless\b", r"\bterri(ble|fying)\b",
    ],
    "hype_promotion": [
        r"\bgame changer\b", r"\bthe future of\b", r"\brevolution\b",
        r"\btransform(ing|ative)\b", r"\bdisrupt(ing|ive|ion)\b",
        r"\bunprecedented\b",
    ],
    "measured_evaluation": [
        r"\bpros and cons\b", r"\bon one hand\b", r"\bbalanced\b",
        r"\btradeoff\b", r"\btrade-off\b", r"\bit depends\b",
        r"\bnuanc\b", r"\bcontext matters\b",
    ],
    "question_seeking": [
        r"\bhas anyone (tried|used|tested)\b", r"\bwhat do you think\b",
        r"\banyone (know|have experience)\b", r"\brecommend\b",
        r"\blooking for advice\b", r"\bshould i\b",
    ],
    "authority_citation": [
        r"\bstudy (shows|found|suggests)\b", r"\baccording to\b",
        r"\bresearch (shows|indicates)\b", r"\bstatistic\b",
        r"\bpeer.?review\b", r"\bpublished in\b",
    ],
}


def classify_frame(text):
    hits = {}
    for frame, patterns in FRAME_PATTERNS.items():
        count = sum(1 for p in patterns if re.search(p, text))
        if count > 0:
            hits[frame] = count
    if not hits:
        return "unframed"
    ranked = sorted(hits.items(), key=lambda x: x[1], reverse=True)
    return ranked[0][0]


# ---------------------------------------------------------------------------
# 4. Community Norm Detection
# ---------------------------------------------------------------------------

def detect_community_norms(df):
    """
    Compare high-score vs low-score posts per theme to surface what
    the community rewards (upvotes) vs punishes (downvotes).
    """
    reddit = df[df["source"] == "reddit"].copy()
    if len(reddit) == 0 or "score" not in reddit.columns:
        return pd.DataFrame()

    reddit["score"] = pd.to_numeric(reddit["score"], errors="coerce")
    reddit = reddit.dropna(subset=["score"])

    norms = []
    for theme in reddit["primary_theme"].dropna().unique():
        subset = reddit[reddit["primary_theme"] == theme]
        if len(subset) < 5:
            continue

        median_score = subset["score"].median()
        rewarded = subset[subset["score"] > median_score]
        punished = subset[subset["score"] <= median_score]

        rewarded_emotions = rewarded["dominant_emotion"].value_counts().head(2).to_dict()
        punished_emotions = punished["dominant_emotion"].value_counts().head(2).to_dict()
        rewarded_frames = rewarded["rhetorical_frame"].value_counts().head(2).to_dict()
        punished_frames = punished["rhetorical_frame"].value_counts().head(2).to_dict()

        norms.append({
            "theme": theme,
            "median_score": median_score,
            "rewarded_emotions": str(rewarded_emotions),
            "punished_emotions": str(punished_emotions),
            "rewarded_frames": str(rewarded_frames),
            "punished_frames": str(punished_frames),
            "rewarded_sentiment_avg": round(rewarded["sentiment_compound"].mean(), 3),
            "punished_sentiment_avg": round(punished["sentiment_compound"].mean(), 3),
        })

    return pd.DataFrame(norms)


# ---------------------------------------------------------------------------
# 5. Narrative Extraction
# ---------------------------------------------------------------------------

NARRATIVE_MARKERS = [
    r"\bi (tried|used|tested|started|switched|moved|decided)\b",
    r"\bwe (implemented|adopted|rolled out|deployed|migrated)\b",
    r"\blast (week|month|year)\b",
    r"\bafter (using|trying|testing)\b",
    r"\bmy experience with\b",
    r"\bhere'?s what happened\b",
    r"\bstory time\b",
    r"\blong story short\b",
]


def is_narrative(text):
    return any(re.search(p, text) for p in NARRATIVE_MARKERS)


def extract_narratives(df, max_per_theme=5):
    """Pull first-person experience stories grouped by theme."""
    narratives = []
    for theme in df["primary_theme"].dropna().unique():
        subset = df[df["primary_theme"] == theme]
        story_mask = subset["clean_text"].apply(is_narrative)
        stories = subset[story_mask].copy()

        if len(stories) == 0:
            continue

        if "score" in stories.columns:
            stories["score"] = pd.to_numeric(stories["score"], errors="coerce")
            stories = stories.sort_values("score", ascending=False)

        for _, row in stories.head(max_per_theme).iterrows():
            narratives.append({
                "theme": theme,
                "speaker_role": row.get("speaker_role", ""),
                "sentiment": row.get("sentiment_label", ""),
                "emotion": row.get("dominant_emotion", ""),
                "excerpt": str(row["clean_text"])[:500],
                "source_url": row.get("source_url", ""),
                "source": row.get("source", ""),
            })

    return pd.DataFrame(narratives)


# ---------------------------------------------------------------------------
# 6. Reflexive Memos
# ---------------------------------------------------------------------------

def generate_reflexive_memos(df, norms_df):
    """
    Generate interpretive memos per theme that synthesize quantitative
    and qualitative signals — closer to netnographic fieldnotes than
    simple frequency reports.
    """
    memos = []
    for theme in df["primary_theme"].dropna().unique():
        subset = df[df["primary_theme"] == theme]
        n = len(subset)
        if n < 3:
            continue

        reddit_n = len(subset[subset["source"] == "reddit"])
        web_n = len(subset[subset["source"] == "web"])

        sentiment_dist = subset["sentiment_label"].value_counts(normalize=True)
        pos_pct = round(sentiment_dist.get("positive", 0) * 100)
        neg_pct = round(sentiment_dist.get("negative", 0) * 100)
        neu_pct = round(sentiment_dist.get("neutral", 0) * 100)

        top_emotion = subset["dominant_emotion"].value_counts().index[0] if len(subset) > 0 else "none"
        top_frame = subset["rhetorical_frame"].value_counts().index[0] if len(subset) > 0 else "unframed"

        role_dist = subset["speaker_role"].value_counts().head(3).to_dict()
        role_str = ", ".join(f"{r} ({c})" for r, c in role_dist.items())

        narrative_count = subset["clean_text"].apply(is_narrative).sum()

        norm_row = norms_df[norms_df["theme"] == theme] if len(norms_df) > 0 else pd.DataFrame()
        norm_note = ""
        if len(norm_row) > 0:
            r = norm_row.iloc[0]
            norm_note = (
                f"Community scoring patterns suggest the community rewards "
                f"{r['rewarded_frames']} framing (avg sentiment {r['rewarded_sentiment_avg']}) "
                f"and is cooler toward {r['punished_frames']} framing "
                f"(avg sentiment {r['punished_sentiment_avg']})."
            )

        memo = (
            f"## {theme}\n\n"
            f"This theme captured {n} items ({reddit_n} Reddit, {web_n} web). "
            f"The emotional tone is predominantly {top_emotion}, with sentiment "
            f"running {pos_pct}% positive, {neg_pct}% negative, {neu_pct}% neutral. "
            f"Contributors most often use a {top_frame} rhetorical frame. "
            f"Speaker roles: {role_str}. "
            f"{narrative_count} posts contain first-person experience narratives, "
            f"suggesting {'active practitioner engagement' if narrative_count > 3 else 'limited experiential grounding'}. "
            f"{norm_note}\n"
        )
        memos.append({"theme": theme, "memo": memo})

    return pd.DataFrame(memos)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_qualitative():
    df = pd.read_csv("data/coded_posts.csv")
    print(f"Loaded {len(df)} coded rows")

    # --- Sentiment ---
    print("\nRunning sentiment analysis...")
    sia = SentimentIntensityAnalyzer()
    sentiment = df["clean_text"].apply(lambda t: get_sentiment(str(t), sia))
    df["sentiment_compound"] = sentiment["sentiment_compound"]
    df["sentiment_label"] = sentiment["sentiment_label"]

    # --- Emotion ---
    print("Detecting emotions...")
    df["dominant_emotion"] = df["clean_text"].apply(lambda t: detect_emotions(str(t)))

    # --- Speaker Role ---
    print("Classifying speaker roles...")
    df["speaker_role"] = df["clean_text"].apply(lambda t: classify_role(str(t)))

    # --- Rhetorical Frame ---
    print("Detecting rhetorical frames...")
    df["rhetorical_frame"] = df["clean_text"].apply(lambda t: classify_frame(str(t)))

    # --- Save enriched data ---
    df.to_csv("data/qualitative_coded.csv", index=False)
    print(f"\nSaved enriched data to data/qualitative_coded.csv")

    # --- Community Norms ---
    print("\nAnalyzing community norms...")
    norms_df = detect_community_norms(df)
    if len(norms_df) > 0:
        norms_df.to_csv("data/community_norms.csv", index=False)
        print(f"Saved community norms to data/community_norms.csv")

    # --- Narratives ---
    print("\nExtracting narratives...")
    narratives_df = extract_narratives(df)
    if len(narratives_df) > 0:
        narratives_df.to_csv("data/narratives.csv", index=False)
        print(f"Extracted {len(narratives_df)} narrative excerpts → data/narratives.csv")

    # --- Reflexive Memos ---
    print("\nGenerating reflexive memos...")
    memos_df = generate_reflexive_memos(df, norms_df)
    if len(memos_df) > 0:
        memos_df.to_csv("data/reflexive_memos.csv", index=False)
        with open("data/reflexive_memos.txt", "w") as f:
            for _, row in memos_df.iterrows():
                f.write(row["memo"] + "\n")
        print(f"Saved {len(memos_df)} reflexive memos → data/reflexive_memos.csv + .txt")

    # --- Summary stats ---
    print(f"\n{'='*60}")
    print("QUALITATIVE LAYER SUMMARY")
    print(f"{'='*60}")

    print(f"\nSentiment Distribution:")
    print(df["sentiment_label"].value_counts().to_string())

    print(f"\nDominant Emotions:")
    print(df["dominant_emotion"].value_counts().to_string())

    print(f"\nSpeaker Roles:")
    print(df["speaker_role"].value_counts().to_string())

    print(f"\nRhetorical Frames:")
    print(df["rhetorical_frame"].value_counts().to_string())

    print(f"\nNarrative Posts: {df['clean_text'].apply(is_narrative).sum()}")

    # --- Print top memos ---
    if len(memos_df) > 0:
        print(f"\n{'='*60}")
        print("REFLEXIVE MEMOS (Top 5 themes)")
        print(f"{'='*60}")
        for _, row in memos_df.head(5).iterrows():
            print(f"\n{row['memo']}")


if __name__ == "__main__":
    run_qualitative()
