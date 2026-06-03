#!/usr/bin/env python3
"""
Build the dataset from web-scraped content.
Since Reddit and ABA block automated scraping, this script constructs
the dataset from content collected via WebSearch + WebFetch tools.
Each item has a verified source_url citation.
"""

import os
import re
import hashlib
import pandas as pd
from datetime import datetime

import nltk
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon", quiet=True)
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ===================================================================
# RAW DATA — collected via WebSearch + WebFetch with citations
# ===================================================================

RAW_ITEMS = [
    # --- Harvey AI / Hallucinations ---
    {
        "title": "Harvey AI hit $8 billion but tools still hallucinate in 1 of 6 queries",
        "body_text": "Harvey reached $8 billion valuation by December 2025, raising nearly $1 billion across six funding rounds. Stanford HAI study found hallucination in roughly 1 of every 6 queries for Lexis+ AI. General-purpose LLMs without legal-specific training fabricated information in over half of responses. AI describes law incorrectly or makes factual errors. AI cites sources that don't actually support its claims. Westlaw claimed false paragraph existed in Federal Rules of Bankruptcy Procedure. Lexis+ AI failed to recognize overruled Supreme Court standard. Database tracks over 850 documented cases worldwide where AI-generated hallucinations affected court filings. Gabriel Pereyra stated One common misconception in legal is that an AI system needs to be 0 hallucinations to be useful. A&O Shearman reports 2-3 hours saved weekly per staff member. David Wakeling said You must validate everything coming out of the system. Industry insiders refer to legal AI products as vaporware. Paul Weiss tested Harvey 18 months without developing hard metrics due to verification burden.",
        "source_url": "https://tao-hpu.medium.com/harvey-ai-hit-8-billion-its-tools-still-hallucinate-in-one-of-every-six-queries-812d64182dc4",
        "source": "web", "source_type": "blog",
    },
    {
        "title": "Harvey AI review 2026 — accuracy and trust concerns",
        "body_text": "Harvey reports a verified citation accuracy rate of 99.7 percent with a policy of flagging any citation it cannot verify with high confidence. Harvey hallucination detection methodology has reduced hallucination rates to approximately 0.2 percent in internal evaluations. Despite these claims hallucinations remain a notable concern. Harvey may produce incorrect citations or fabricated case law and without fact-checking these errors can pose real malpractice risks. The most consistent criticism across independent reviews centres on the accuracy gaps in specialized or emerging areas of law and the fact that every output still requires substantive human verification before it goes anywhere near a client. Harvey uses agentic workflows to catch and correct hallucinations in real time with AI agents performing self-review deeper research and escalation to human experts when needed.",
        "source_url": "https://growlaw.co/blog/harvey-ai-review",
        "source": "web", "source_type": "blog",
    },
    # --- Mata v. Avianca ---
    {
        "title": "Mata v Avianca — attorneys cited 6 fabricated cases from ChatGPT",
        "body_text": "In Mata v Avianca 2023 attorneys cited 6 fabricated cases to federal court. ChatGPT assured lawyers cases indeed exist in legal databases. Judge imposed $5000 in sanctions and found subjective bad faith. This case became the landmark example of AI hallucination risks in litigation. It demonstrated the danger of relying on AI-generated legal citations without verification. The case sparked nationwide discussion about lawyer competence obligations when using AI tools.",
        "source_url": "https://tao-hpu.medium.com/harvey-ai-hit-8-billion-its-tools-still-hallucinate-in-one-of-every-six-queries-812d64182dc4",
        "source": "web", "source_type": "news",
    },
    # --- 16 Tech Leaders ---
    {
        "title": "Legal AI unfiltered: 16 tech leaders on replacing lawyers",
        "body_text": "Scott Stevenson of Spellbook said AI will not replace lawyers because even if you can automate legal work clients cannot understand what the documents you produce mean. Daniel Lewis of LegalOn said AI will transform how lawyers work rather than eliminate them enabling focus on judgment and strategy. Gil Banyas of Chamelio said AI will not replace lawyers but will reduce numbers needed as routine work automates. Arunim Samat of TrueLaw said AI will create 10x lawyers accomplishing far more work. Chris Williams of Leya said lawyers using AI will replace those who do not adopt it. Small and mid-sized firms already moving to flat-fee billing with substantially increased margins. Billable hour faces significant pressure with flat fees and subscriptions becoming more common. Multiple firms using Briefpoint switched to flat rates on automated discovery tasks.",
        "source_url": "https://natlawreview.com/article/legal-ai-unfiltered-16-tech-leaders-ai-replacing-lawyers-billable-hour-and",
        "source": "web", "source_type": "news",
    },
    {
        "title": "Tech leaders on AI hallucinations in legal — solvable or inherent",
        "body_text": "Hallucinations occur when AI attempts impossible tasks and achievable tasks with correct info prevent them according to Spellbook. Complete elimination may be unrealistic but substantial reduction achievable through grounding AI in authoritative legal content says LegalOn. Some hallucination occurs in human reasoning too and errors are fundamental to complex tasks says PointOne. LLMs are probabilistic by nature and hallucinations are use-case-specific and grounding techniques minimize risk nearly to zero but cannot guarantee elimination. Hallucinations are inherent to LLMs but manageable with comprehensive systems. Greg Siskind predicts the problem persists several years at diminishing rates and largely disappears within approximately five years. Human verification remains mandatory for all AI-generated legal citations summaries and drafts before external sharing.",
        "source_url": "https://natlawreview.com/article/legal-ai-unfiltered-16-tech-leaders-ai-replacing-lawyers-billable-hour-and",
        "source": "web", "source_type": "news",
    },
    {
        "title": "Tech leaders on law firm AI adoption hesitation",
        "body_text": "Small and mid-sized firms show almost no hesitation while larger firms are secretly hesitant due to billable hour model says Spellbook. Firms hesitant over risk and liability concerns with accuracy and confidentiality mattering most says LegalOn. Only 10 percent of law firms have generative AI policies and fewer possess clear strategies. Fear dominates and perfect is currently the enemy of good mindset is subsiding gradually. Number one reason for hesitation is lack of urgency from billable hour business model eliminating immediate financial incentive for efficiency. Data privacy and hallucinations are most common concerns. Lawyers want assurance data will not train models and outputs remain reliable. Trust is the primary issue as lawyers need confidence and AI feels like a black box.",
        "source_url": "https://natlawreview.com/article/legal-ai-unfiltered-16-tech-leaders-ai-replacing-lawyers-billable-hour-and",
        "source": "web", "source_type": "news",
    },
    # --- Adoption stats ---
    {
        "title": "Law firm AI adoption curve — 78 percent not using AI",
        "body_text": "78 percent of US law firms were not using any AI tools as of year-end 2024. Legal organizations actively integrating generative AI rose from 14 percent in 2024 to 26 percent in 2025. 45 percent of law firms either use AI or plan to make it central to workflows within one year. Firms with 51 or more attorneys use AI at roughly double the rate of smaller firms. 41 percent of surveyed lawyers reported concerns about data privacy related to AI adoption. June 2023 New York attorneys fined $5000 for submitting briefs with six fictitious ChatGPT-generated cases. Custom low-code solutions can cost approximately $10000 total versus $600 per month subscriptions. 40 percent of law firm respondents believe AI will increase non-hourly billing methods. Risk-averse legal culture continues questioning whether to use AI at all.",
        "source_url": "https://www.bestlawfirms.com/articles/the-ai-adoption-curve-in-law/6934",
        "source": "web", "source_type": "news",
    },
    {
        "title": "AI adoption rates in law — from 19 to 79 percent in one year",
        "body_text": "In 2024 31 percent of legal professionals personally used generative AI for work up from 27 percent in 2023 while only 21 percent of law firms had adopted it. Broader AI adoption is higher with overall AI use among lawyers beyond just generative AI shooting up from 19 to 79 percent between 2023 and 2024. 2024 marked a record-breaking year for legal-tech startups which raised $4.98 billion overall largely propelled by the booming interest in AI. Trust and ethical considerations are major roadblocks to wider AI adoption among law firms.",
        "source_url": "https://www.netdocuments.com/blog/ai-driven-legal-tech-trends-for-2025/",
        "source": "web", "source_type": "blog",
    },
    # --- eDiscovery ---
    {
        "title": "AI in ediscovery — 41 percent of firms cite discovery as top challenge",
        "body_text": "Courts widely accept the use of AI and Technology-Assisted Review TAR in eDiscovery as long as it is transparent and defensible. 41 percent of firms said managing discovery was one of their top efficiency challenges in litigation workflows. AI rapidly identifies the most responsive or potentially privileged documents shifting lawyers focus from sifting to strategic action. Modern AI platforms can surface crucial data in diverse formats including multimedia and chat logs. Key clauses deadlines or red flags are surfaced for human review reducing the risk of oversight. AI enhances efficiency but still requires human oversight with final privilege calls and key case decisions always involving legal professionals.",
        "source_url": "https://www.casepoint.com/resources/spotlight/generative-ai-in-ediscovery-transforming-legal-document-review/",
        "source": "web", "source_type": "blog",
    },
    # --- Deposition prep ---
    {
        "title": "AI deposition preparation — from overload to clarity",
        "body_text": "AI synthesizes scattered facts notes and documents into coherent case summaries for deposition prep. Generates draft outlines with topic buckets and questioning threads. Creates post-deposition recaps noting admissions and follow-up items. Reduces hours or weeks of manual synthesis to fraction of the time. Produces structured summaries linked to source materials with page and line citations. Identifies key themes contradictions and gaps in witness statements. Lawyers worry that AI may misinterpret transcripts or miss subtle details. Concerns about confidentiality and sensitive data exposure remain. Use trusted firm-approved platforms and request cited outputs with source references. Verify key facts against original records.",
        "source_url": "https://www.clio.com/resources/ai-for-lawyers/deposition-prep-ai/",
        "source": "web", "source_type": "blog",
    },
    # --- Ethics and bar guidance ---
    {
        "title": "2025 state bar AI guidance — over 30 states issue rules",
        "body_text": "ABA Formal Opinion 512 establishes national baseline requiring lawyers maintain competence confidentiality transparency and reasonable fees when using AI tools. Over 30 states have released AI-specific guidance creating compliance patchwork requiring flexible policies. Pennsylvania requires explicit disclosure of AI use in all court submissions. New York requires minimum two annual CLE credits in practical AI competency by Q3 2025. Human verification mandatory for all AI-generated legal citations summaries and drafts before external sharing. Encrypted verification logs must be maintained minimum seven years. Firms should classify AI uses as Red Light prohibited Yellow Light cautious or Green Light standard. Dedicated AI Governance Committee should meet quarterly to review risks and audit usage logs. Lawyers remain fully responsible for all legal work regardless of AI involvement.",
        "source_url": "https://www.paxton.ai/post/2025-state-bar-guidance-on-legal-ai",
        "source": "web", "source_type": "blog",
    },
    {
        "title": "ABA Task Force says AI moved from experiment to infrastructure",
        "body_text": "The ABA 2025 AI Task Force Year Two Report highlights rapid increase in formal guidance across jurisdictions reflecting growing consensus that AI can be used responsibly. 80 percent of AmLaw 100 firms have now established AI governance boards moving from experimental adoption to enterprise-wide transformation. AI systems frequently produce incomplete or inaccurate results. Confidentiality risks have evolved beyond traditional cloud security concerns. The profession still lacks robust frameworks for bias detection and mitigation. Lawyers do not need to become AI experts but they must develop a reasonable understanding of the capabilities and limitations of the specific AI technology they use.",
        "source_url": "https://www.lawnext.com/2025/12/aba-task-force-ai-has-moved-from-experiment-to-infrastructure-for-the-legal-profession.html",
        "source": "web", "source_type": "news",
    },
    # --- Cost and ROI ---
    {
        "title": "Legal AI pricing — $40 to $400 per user per month",
        "body_text": "Most legal AI platforms cost $40 to $150 per user per month depending on features and automation capabilities with AI-enabled tiers typically starting around $120 per user. CoCounsel $225 plus Westlaw $200 pushes total spend north of $400 per month. A mid-sized law firm billing $350 per hour with an AI solution that saves 20 hours weekly could deliver $364000 in annual value. Organizations with visible AI strategies are 3.9 times more likely to see ROI. Law firms typically expect ROI from legal technology investments within 12-18 months. Integration complexity can add 15-30 percent to the effective cost of legal AI implementation. Subscription models recognize that many clients need continuous access to legal expertise.",
        "source_url": "https://elephas.app/resources/legal-ai-tools-pricing-comparison",
        "source": "web", "source_type": "blog",
    },
    {
        "title": "Law firm AI ROI — what finally worked in 2025",
        "body_text": "Law firm AI ROI what finally worked and why in 2025. The discussion is shifting from whether to adopt AI to the risks of not adopting it. Firms that established clear AI strategies saw 3.9 times better ROI outcomes. Small firms face cost of implementation difficulty finding suitable products for their scale and fear that investments will be quickly rendered obsolete. The reality of AI impact has fallen short of early expectations with most attorneys observing limited effects during 2024-2025. American firms with 51 attorneys or more are using AI at roughly double the rate of firms with fewer lawyers creating an adoption divide.",
        "source_url": "https://www.bestlawfirms.com/articles/law-firm-ai-roi-what-finally-worked-and-why-in-2025/7229",
        "source": "web", "source_type": "news",
    },
    # --- Job displacement ---
    {
        "title": "AI might not be coming for lawyers jobs anytime soon — MIT",
        "body_text": "AI might not be coming for lawyers jobs anytime soon according to MIT Technology Review. LLMs are still far from thinking like lawyers as the models continue to hallucinate case citations struggle to navigate gray areas of the law and reason about novel questions. 69 percent of hourly billable work performed by paralegals could be automated by AI but paralegals achieved a 50 percent time savings on administrative tasks suggesting efficiency gains rather than elimination of roles. AI will not replace lawyers but lawyers who use AI will replace those who do not. Paralegals are increasingly responsible for managing workflows that involve both humans and legal AI tools reviewing outputs generated by AI and ensuring accuracy.",
        "source_url": "https://www.technologyreview.com/2025/12/15/1129181/ai-might-not-be-coming-for-lawyers-jobs-anytime-soon/",
        "source": "web", "source_type": "news",
    },
    # --- AI tools list ---
    {
        "title": "11 AI tools for lawyers — Clio survey shows 79 percent use AI",
        "body_text": "79 percent of legal professionals surveyed in Clio Legal Trends Report use AI in some capacity at their firms. Tools include Clio Work for research and drafting powered by Vincent AI, Manage AI for practice management and deadline extraction, Diligen for machine learning contract review and due diligence, Darrow AI for detecting potential legal violations using generative AI, Eudia platform for large legal teams with $105M Series A funding, Supio AI for personal injury firms with medical chronology automation. Small firms using ChatGPT or general-purpose AI while larger firms investing in purpose-built legal AI platforms. Integration with existing practice management systems is a key differentiator.",
        "source_url": "https://www.clio.com/resources/ai-for-lawyers/ai-tools-for-lawyers/",
        "source": "web", "source_type": "blog",
    },
    # --- Predictions ---
    {
        "title": "85 predictions for AI and the law in 2026",
        "body_text": "85 predictions for AI and the law in 2026 from National Law Review. AI-driven legal tech trends show continued growth with firms moving from pilot programs to enterprise-wide deployment. The legal industry report 2025 shows significant acceleration in AI adoption across practice areas including litigation contract review and legal research. Forward-thinking litigation teams are leveraging AI-powered predictive analytics to analyze vast datasets of past cases judges and opposing counsel behaviors identifying patterns such as a judges ruling tendencies or expert witness success rates. AI tools offer data-driven predictions on case outcomes providing lawyers with valuable insights for strategic planning.",
        "source_url": "https://natlawreview.com/article/85-predictions-ai-and-law-2026",
        "source": "web", "source_type": "news",
    },
]


# ===================================================================
# Theme coding
# ===================================================================

THEME_KEYWORDS = {
    "accuracy_trust": [
        "hallucinate", "hallucination", "wrong", "inaccurate", "trust",
        "reliable", "mistake", "error", "accuracy", "unreliable",
        "fabricat", "verified", "verification", "malpractice",
    ],
    "ediscovery_review": [
        "ediscovery", "e-discovery", "document review", "review platform",
        "relativity", "nuix", "logikcull", "disco", "predictive coding",
        "tar", "technology assisted", "privilege review",
    ],
    "deposition_trial": [
        "deposition", "trial", "courtroom", "witness", "cross-examin",
        "testimony", "prep", "exhibit", "hearing", "motion", "sanctions",
    ],
    "efficiency_gains": [
        "fast", "speed", "efficient", "productive", "save time", "workflow",
        "automate", "streamline", "hours saved", "minutes", "billable",
    ],
    "job_displacement": [
        "replace", "replacing", "job", "unemploy", "displace", "obsolete",
        "hire", "layoff", "workforce", "paralegal", "associate",
    ],
    "cost_value": [
        "cost", "expensive", "cheap", "pricing", "worth", "afford",
        "fee", "subscription", "budget", "roi", "value", "per month",
    ],
    "tool_review": [
        "harvey", "legora", "casetext", "lexis", "westlaw", "copilot",
        "chatgpt", "claude", "gemini", "clio", "litify", "vlex",
        "spellbook", "cocounsel", "diligen", "darrow",
    ],
    "ethics_regulation": [
        "regulat", "compli", "bar association", "unauthorized practice",
        "upl", "govern", "ethical", "bias", "fairness", "oversight",
        "aba", "formal opinion", "disclosure", "competence",
    ],
    "adoption_resistance": [
        "adopt", "resist", "refuse", "skeptic", "hesitan", "barrier",
        "not using", "reluctan", "black box", "fear", "cautious",
    ],
}

EMOTION_LEXICON = {
    "frustration": ["frustrat", "annoying", "ridiculous", "useless", "waste", "terrible", "awful", "sucks", "disappointed"],
    "enthusiasm": ["amazing", "love", "incredible", "game changer", "revolutionary", "excited", "impressive", "fantastic", "awesome"],
    "anxiety": ["worried", "scary", "terrif", "concern", "afraid", "threat", "nervous", "uncertain", "alarming"],
    "skepticism": ["doubt", "skeptic", "overhyp", "hype", "snake oil", "gimmick", "marketing", "buzzword", "vaporware"],
    "pragmatism": ["practical", "useful", "helpful", "works well", "saved", "in practice", "workflow", "actually", "real world"],
}

ROLE_PATTERNS = {
    "practitioner": [r"\bmy firm\b", r"\bour firm\b", r"\bmy clients\b", r"\bat my firm\b", r"\bin my practice\b", r"\blawyer\b", r"\battorney\b"],
    "law_student": [r"\blaw student\b", r"\blaw school\b", r"\bbar exam\b"],
    "vendor_builder": [r"\bwe built\b", r"\bour product\b", r"\bour tool\b", r"\bour platform\b", r"\bco-?founder\b"],
    "tech_leader": [r"\bceo\b", r"\bcto\b", r"\bfounder\b", r"\bleader\b"],
    "industry_analyst": [r"\breport\b", r"\bsurvey\b", r"\bstudy\b", r"\bfound that\b", r"\baccording to\b"],
}

FRAME_PATTERNS = {
    "lived_experience": [r"\bi (tried|used|tested)\b", r"\bin my experience\b", r"\bwhen i used\b"],
    "fear_warning": [r"\bdangerous\b", r"\breckless\b", r"\brisk\b", r"\bsanctions\b"],
    "hype_promotion": [r"\bgame changer\b", r"\bthe future of\b", r"\brevolution\b", r"\btransform\b"],
    "measured_evaluation": [r"\bpros and cons\b", r"\bit depends\b", r"\bnuanc\b", r"\bboth\b"],
    "data_driven": [r"\bpercent\b", r"\bstudy\b", r"\bsurvey\b", r"\breport\b", r"\bstatistic\b"],
    "question_seeking": [r"\bhas anyone\b", r"\bwhat do you think\b", r"\brecommend\b", r"\bshould\b"],
}

NARRATIVE_MARKERS = [
    r"\bi (tried|used|tested|started|switched)\b",
    r"\bwe (implemented|adopted|rolled out|deployed)\b",
    r"\bafter (using|trying|testing)\b",
    r"\bmy experience\b",
]


def clean_text(text):
    text = text.lower()
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[^a-z0-9\s.,!?'\"-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_dataset():
    print("Building dataset from collected web content...")

    rows = []
    for item in RAW_ITEMS:
        rid = hashlib.md5(item["source_url"].encode() + item["title"].encode()).hexdigest()[:12]
        rows.append({
            "id": rid,
            "source": item["source"],
            "source_type": item["source_type"],
            "subreddit": "",
            "title": item["title"],
            "body_text": item["body_text"],
            "author": "",
            "score": 0,
            "num_comments": 0,
            "created_date": "",
            "source_url": item["source_url"],
            "post_type": "article",
        })

    df = pd.DataFrame(rows)
    df["clean_text"] = df["body_text"].apply(clean_text)
    df = df[df["clean_text"].str.len() >= 20]
    df.to_csv(os.path.join(DATA_DIR, "raw_combined.csv"), index=False)
    df.to_csv(os.path.join(DATA_DIR, "cleaned_posts.csv"), index=False)

    # --- Theme coding ---
    def assign(text):
        scores = {t: sum(1 for kw in kws if kw in text) for t, kws in THEME_KEYWORDS.items()}
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = ranked[0] if ranked[0][1] > 0 else ("uncategorized", 0)
        secondary = ranked[1] if len(ranked) > 1 and ranked[1][1] >= 2 else (None, 0)
        return primary[0], secondary[0], primary[1]

    results = df["clean_text"].apply(lambda t: pd.Series(assign(t), index=["primary_theme", "secondary_theme", "primary_hits"]))
    df = pd.concat([df.reset_index(drop=True), results], axis=1)
    df["theme_confidence"] = "keyword"
    df.to_csv(os.path.join(DATA_DIR, "coded_posts.csv"), index=False)

    # --- Qualitative ---
    sia = SentimentIntensityAnalyzer()

    def get_sent(text):
        s = sia.polarity_scores(str(text))
        label = "positive" if s["compound"] >= 0.05 else ("negative" if s["compound"] <= -0.05 else "neutral")
        return s["compound"], label

    sent = df["clean_text"].apply(lambda t: pd.Series(get_sent(t), index=["sentiment_compound", "sentiment_label"]))
    df["sentiment_compound"] = sent["sentiment_compound"]
    df["sentiment_label"] = sent["sentiment_label"]

    def detect_emotion(text):
        hits = {e: sum(1 for kw in kws if kw in str(text)) for e, kws in EMOTION_LEXICON.items()}
        hits = {k: v for k, v in hits.items() if v > 0}
        return max(hits, key=hits.get) if hits else "none"

    df["dominant_emotion"] = df["clean_text"].apply(detect_emotion)

    def classify_role(text):
        for role, patterns in ROLE_PATTERNS.items():
            if any(re.search(p, str(text)) for p in patterns):
                return role
        return "unidentified"

    df["speaker_role"] = df["clean_text"].apply(classify_role)

    def classify_frame(text):
        hits = {f: sum(1 for p in pats if re.search(p, str(text))) for f, pats in FRAME_PATTERNS.items()}
        hits = {k: v for k, v in hits.items() if v > 0}
        return max(hits, key=hits.get) if hits else "unframed"

    df["rhetorical_frame"] = df["clean_text"].apply(classify_frame)

    df["is_narrative"] = df["clean_text"].apply(
        lambda t: any(re.search(p, str(t)) for p in NARRATIVE_MARKERS)
    )

    df.to_csv(os.path.join(DATA_DIR, "qualitative_coded.csv"), index=False)

    # --- Theme summary ---
    total = len(df)
    themes = df["primary_theme"].value_counts()
    summary = []
    for theme, count in themes.items():
        subset = df[df["primary_theme"] == theme]
        pct = round(count / total * 100, 1)
        excerpts = []
        for _, row in subset.head(3).iterrows():
            excerpts.append({"text": str(row["clean_text"])[:300], "url": row.get("source_url", ""), "title": row.get("title", "")})
        while len(excerpts) < 3:
            excerpts.append({"text": "", "url": "", "title": ""})

        sdist = subset["sentiment_label"].value_counts(normalize=True)
        pos = round(sdist.get("positive", 0) * 100)
        neg = round(sdist.get("negative", 0) * 100)
        top_emo = subset["dominant_emotion"].value_counts().index[0] if len(subset) > 0 else "none"
        top_frame = subset["rhetorical_frame"].value_counts().index[0] if len(subset) > 0 else "unframed"

        summary.append({
            "theme": theme, "count": count, "percentage": pct,
            "sentiment_positive_pct": pos, "sentiment_negative_pct": neg,
            "top_emotion": top_emo, "top_frame": top_frame,
            "excerpt_1": excerpts[0]["text"], "excerpt_1_url": excerpts[0]["url"], "excerpt_1_title": excerpts[0]["title"],
            "excerpt_2": excerpts[1]["text"], "excerpt_2_url": excerpts[1]["url"], "excerpt_2_title": excerpts[1]["title"],
            "excerpt_3": excerpts[2]["text"], "excerpt_3_url": excerpts[2]["url"], "excerpt_3_title": excerpts[2]["title"],
        })

    pd.DataFrame(summary).to_csv(os.path.join(DATA_DIR, "themes_summary.csv"), index=False)

    # --- Narratives ---
    narr_rows = []
    for theme in df["primary_theme"].dropna().unique():
        subset = df[(df["primary_theme"] == theme) & (df["is_narrative"])]
        for _, row in subset.head(3).iterrows():
            narr_rows.append({
                "theme": theme, "speaker_role": row["speaker_role"],
                "sentiment": row["sentiment_label"], "emotion": row["dominant_emotion"],
                "excerpt": str(row["clean_text"])[:500],
                "source_url": row.get("source_url", ""), "source": row["source"],
                "title": row.get("title", ""),
            })
    pd.DataFrame(narr_rows).to_csv(os.path.join(DATA_DIR, "narratives.csv"), index=False)

    print(f"  Items: {len(df)}")
    print(f"  Themes: {df['primary_theme'].nunique()}")
    print(f"  Sentiment: {df['sentiment_label'].value_counts().to_dict()}")
    print(f"  Emotions: {df['dominant_emotion'].value_counts().to_dict()}")
    print(f"  Saved to {DATA_DIR}/")


if __name__ == "__main__":
    build_dataset()
