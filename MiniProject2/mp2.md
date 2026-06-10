# MP2 Competency Claims: DocketSignal

These are the competency claims I am making for Mini Project 2. DocketSignal is my tool for turning public legal-AI discourse into themes, evidence excerpts, memos, and product-facing research signals.

## C8 - Building and Deploying a Complete Tool

### What I built

I built DocketSignal, a small public dashboard and Python pipeline for reading legal-AI discourse on Reddit. The use case is simple: a legal-tech researcher or UX researcher can look at public conversations and quickly see what people are worried about, such as fake citations, confidentiality, billing pressure, governance, junior lawyer anxiety, and workflow fit.

### Where the evidence is

The public tool is in `MiniProject2/index.html`. The supporting pages are `design.html`, `competencies.html`, and `reflection.html`. The pipeline and outputs are in `src/`, `data/`, and `outputs/`. The README explains how to run the sample version and how to connect Reddit credentials for live collection.

### What I learned

A complete tool needs code that runs and a clear front door for someone who did not build it. I added the dashboard because a CSV-only project would make the user do too much work before understanding the point of the project.

## C4 - APIs and Data Acquisition

### What I built

I added a live Reddit collection path using PRAW in `src/collect_reddit.py`. The script can pull public posts and comments from selected legal and AI-related subreddits, then pass those rows into the same analysis pipeline as the sample data.

### Where the evidence is

The API code is in `src/collect_reddit.py`. The local credential pattern is documented in `.env.template` and the README. The project does not commit Reddit keys. The dashboard keeps source context visible through fields like subreddit, source type, score, and source link.

### What I learned

The data source matters as much as the analysis. Reddit is useful because it has public practitioner-style discussion, but it is still a partial view. I treat it as public discourse data, not as a full picture of the legal profession.

## C3 - Data Cleaning and File Handling

### What I built

I built a repeatable pipeline that turns messy text rows into consistent CSV outputs. The pipeline handles sample loading or live collection, text cleanup, empty-row checks, deduplication, theme assignment, excerpt selection, and output writing.

### Where the evidence is

The main evidence is `src/pipeline.py`. The output files include `data/processed_corpus.csv`, `data/qualitative_corpus.csv`, `outputs/theme_summary.csv`, `outputs/illustrative_excerpts.csv`, and `outputs/memos.md`.

### What I learned

If the rows are inconsistent, every later chart or memo becomes weaker. I wanted the project to leave an audit trail, so the cleaned corpus and the coded corpus are both saved instead of only showing the final dashboard.

## C5 - Data Analysis with Pandas

### What I built

I used the corpus to answer practical analysis questions: which legal-AI themes show up most often, which excerpts support each theme, and what source context sits behind each claim. The analysis produces theme counts, percentages, example excerpts, and summary memos.

### Where the evidence is

The analysis logic is in `src/pipeline.py` and `src/qualitative.py`. The outputs are in `outputs/theme_summary.csv`, `outputs/illustrative_excerpts.csv`, and `outputs/memos.md`.

### What I learned

The count is only a starting point. A theme with a high count tells me where the discourse is concentrated, but the excerpt tells me what the concern actually sounds like. That is why the dashboard keeps counts and evidence together.

## C6 - Data Visualization

### What I built

I used the dashboard to visualize theme rankings and corpus signals. The chart choice is intentionally simple because the theme labels are long and the goal is comparison. A ranked bar-style view is easier to read than a complicated chart for this kind of data.

### Where the evidence is

The visual interface is in `index.html`, `styles.css`, `showcase-data.js`, and the generated chart output in `outputs/`. The dashboard also includes evidence panels so the viewer can move from a chart to the actual excerpts.

### What I learned

A chart should match the shape of the summary table. For DocketSignal, I care more about whether a reader can see the top concerns and then check the evidence.

## C7 - Critical Evaluation and Professional Judgment

### What I built

I kept the tool scoped as research support. It does not present Reddit posts as verified facts, legal advice, or a complete view of legal practice. It gives a researcher a first pass on public discourse and keeps enough context visible for checking.

### Where the evidence is

The README, `reflection.md`, `design.html`, and dashboard copy all describe the limits of the project. The evidence panels show source type and excerpts so a viewer can inspect the basis for a theme.

### What I learned

This is where my law and UX research background meet. From law, I ask what supports the claim and what risk might be hidden. From UX research, I ask who needs the claim and what decision it helps them make. The strongest version of this project is the trace from theme, to excerpt, to source context, to product implication.

## C2 - Code Literacy and Documentation

### What I built

I packaged the project so someone else can understand it without asking me to explain every file. The README explains what the tool does, who it is for, how to run it, how live Reddit collection works, and where the public version is.

### Where the evidence is

The documentation is in `README.md`, `mp2.md`, `reflection.md`, `.env.template`, and the comments/docstrings inside the Python files. The notebook and generated CSVs also make the workflow easier to inspect.

### What I learned

Documentation is part of the tool. If a future collaborator cannot tell what the input is, what the output is, and what the limits are, then the tool is not really usable. I tried to write the docs so a person outside this class could still understand the project.
