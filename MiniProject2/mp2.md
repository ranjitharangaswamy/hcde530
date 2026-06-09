# MP2 Competency Claims: DocketSignal

These are the claims I am making for MP2. I am naming the files and outputs because I want the work to be checkable and specific.

## Claim 1: I can build a computational pipeline that turns messy public text into usable research material.

What I did: I built a Python pipeline that takes public legal-AI discussion and turns it into structured outputs. The main work is in `src/pipeline.py`. It handles collection or sample loading, cleaning, deduplication, theme coding, excerpt selection, memo generation, chart creation, and dashboard export.

Where it shows up: the pipeline creates files like `data/processed_corpus.csv`, `data/qualitative_corpus.csv`, `outputs/theme_summary.csv`, `outputs/illustrative_excerpts.csv`, and `outputs/memos.md`.

Why this matters: the dashboard is backed by a repeatable process instead of hand-written examples. I can rerun the project with sample data or live Reddit credentials and get a new set of research artifacts.

## Claim 2: I can make careful data-scope decisions when working with public discourse.

What I did: I limited the live collection path to public Reddit posts and comments through the official Reddit API using PRAW in `src/collect_reddit.py`. I did not use private forums, client documents, locked communities, or scraped legal matters. I also kept the project clear that it is a research tool and not legal advice.

Where it shows up: the README explains the Reddit source scope, the `.env.template` shows how credentials are handled locally, and `provenance.js` keeps source information visible in the dashboard.

Why this matters: legal-tech research can easily drift into sensitive data. I wanted the project to stay inside a public, inspectable, and lower-risk data boundary. That choice also makes the project easier for someone else to run and evaluate.

## Claim 3: I can use computational methods to support qualitative interpretation.

What I did: I used transparent keyword themes for legal-AI discourse and a TF-IDF/KMeans fallback for rows that do not match the first pass. `src/qualitative.py` adds sentiment, emotion, and rhetorical-frame tags. I treated those outputs as starting points for interpretation, not as final truth.

Where it shows up: the coded corpus, theme table, illustrative excerpts, and memo file all connect counts back to rows and excerpts. The dashboard keeps excerpts close to each theme so the viewer can inspect what the code is based on.

Why this matters: this connects to the Charmaz-style work I wanted to practice. The computer helps sort and surface patterns, but the researcher still has to compare excerpts, question the theme labels, and decide what the pattern means.

## Claim 4: I can design an interface that makes analysis legible to someone outside the class.

What I did: I built a static dashboard in `index.html`, `styles.css`, and the supporting JavaScript files. It shows the project title, corpus context, ranked themes, evidence excerpts, memos, charts, and data exploration. I also added design thinking, competency, and reflection pages so the showcase explains the work behind the interface.

Where it shows up: the dashboard lets someone move from a high-level theme to supporting excerpts and source links. The evidence panels keep source type and context visible instead of hiding the material behind a single summary.

Why this matters: my goal was to make the project understandable in a gallery setting. Someone should be able to see quickly that this is legal-tech discourse intelligence, then inspect the evidence if they want to know how the claim was made.

## Claim 5: I can package a project so another person can run, inspect, and evaluate it.

What I did: I included the code, generated data outputs, notebook, README, `.env.template`, `requirements.txt`, `mp2.md`, and `reflection.md`. The README explains what the tool does, who it is for, how to run the sample path, how to enable live Reddit collection, and where to view the public dashboard.

Where it shows up: the project can be reviewed through the static site, the notebook, the CSV files, or the Python scripts. The same project has both a polished front door and inspectable source files.

Why this matters: a clear deliverable needs more than a working script. It needs enough documentation that another person can understand the scope, reproduce the output, and see what decisions shaped the final artifact.

## Claim 6: I can merge legal reasoning with UX research to frame a product-relevant research question.

What I did: I used legal reasoning to decide which signals mattered: citation trust, hallucinated cases, confidentiality, professional responsibility, billing pressure, sanctions risk, governance, and adoption inside firms. I used UX research methods to turn those public conversations into themes, evidence panels, memos, and product implications.

Where it shows up: the design thinking page explains this cross-discipline stance directly. The dashboard also reflects it through source links, short excerpts, subreddit context, scores, and memos that connect user concerns to product decisions.

Why this matters: this is the part of the project that feels most like my own work. Law trained me to ask what supports a claim and what risk sits behind it. UX research trained me to ask who needs the claim, what decision it helps with, and how to make the evidence easier to inspect. DocketSignal sits at that overlap.
