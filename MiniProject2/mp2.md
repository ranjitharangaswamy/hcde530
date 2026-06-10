# MP2 Competency Claims: DocketSignal

These are the competency claims I am making for Mini Project 2. DocketSignal is my tool for turning public legal-AI discourse into themes, evidence excerpts, memos, and product-facing research signals.

## C8 - Building and Deploying a Complete Tool

### What I built

I built DocketSignal, a small public dashboard and Python pipeline for reading legal-AI discourse on Reddit. The use case is simple: a legal-tech researcher or UX researcher can look at public conversations and quickly see what people are worried about, such as fake citations, confidentiality, billing pressure, governance, junior lawyer anxiety, and workflow fit.

### Where the evidence is

The public version is at `https://ranjitharangaswamy.com/DocketSignal/`. The GitHub Pages fallback is `https://ranjitharangaswamy.github.io/DocketSignal/`. The local tool is in `MiniProject2/index.html`, with supporting pages in `design.html`, `competencies.html`, and `reflection.html`. The pipeline and outputs are in `src/`, `data/`, and `outputs/`.

### What I learned

The first version was mostly pipeline outputs. It technically worked. It still did not explain the use case fast enough. I added the dashboard because a CSV-only version would make the reader do too much work before seeing why the project matters.

## C4 - APIs and Data Acquisition

### What I built

I added a live Reddit collection path using PRAW in `src/collect_reddit.py`. The script can pull public posts and comments from selected legal and AI-related subreddits, then pass those rows into the same analysis pipeline as the sample data. I also kept a sample corpus path so the project still runs without my Reddit credentials.

### Where the evidence is

The API code is in `src/collect_reddit.py`. The local credential pattern is documented in `.env.template` and the README. The project does not commit Reddit keys. The dashboard keeps source context visible through fields like subreddit, source type, score, and source link.

### What I learned

The problem I had to solve was live data without exposing keys or breaking the project for someone else. I kept credentials in `.env`, documented the setup in the README, and kept the sample fallback. Reddit gives public examples of how people talk about legal AI, but I would not treat those posts as representative of the whole legal profession.

## C3 - Data Cleaning and File Handling

### What I built

I built a repeatable pipeline that turns messy text rows into consistent CSV outputs. The pipeline handles sample loading or live collection, text cleanup, empty-row checks, deduplication, theme assignment, excerpt selection, and output writing.

### Where the evidence is

The main evidence is `src/pipeline.py`. The output files include `data/processed_corpus.csv`, `data/qualitative_corpus.csv`, `outputs/theme_summary.csv`, `outputs/illustrative_excerpts.csv`, and `outputs/memos.md`.

### What I learned

The data problem here is that Reddit text is uneven: titles, comments, scores, subreddits, and links do not arrive as a clean research table. If those rows are inconsistent, every later chart or memo becomes weaker. I saved the cleaned corpus and coded corpus so the dashboard is not the only place where the work can be checked.

## C5 - Data Analysis with Pandas

### What I built

I used the corpus to answer practical analysis questions: which legal-AI themes show up most often, which excerpts support each theme, and what source context sits behind each claim. The analysis produces theme counts, percentages, example excerpts, and summary memos.

### Where the evidence is

The analysis logic is in `src/pipeline.py` and `src/qualitative.py`. The outputs are in `outputs/theme_summary.csv`, `outputs/illustrative_excerpts.csv`, and `outputs/memos.md`.

### What I learned

The analysis decision was to keep counts next to excerpts. A theme with a high count tells me where the discourse is concentrated. The excerpt tells me what the concern actually sounds like. Without the excerpt, the theme label can sound more certain than it should.

## C6 - Data Visualization

### What I built

I used the dashboard to visualize theme rankings and corpus signals. The chart choice is intentionally simple because the theme labels are long and the goal is comparison. A ranked bar-style view is easier to read than a complicated chart for this kind of data.

### Where the evidence is

The visual interface is in `index.html`, `styles.css`, `showcase-data.js`, and the generated chart output in `outputs/`. The dashboard also includes evidence panels so the viewer can move from a chart to the actual excerpts.

### What I learned

I avoided a more decorative chart because it would make the project look more analytical than the data supports. The chart has one job here: show which concerns rise to the top without hiding the evidence.

## C7 - Critical Evaluation and Professional Judgment

### What I built

I kept the tool scoped as research support. It does not present Reddit posts as verified facts, legal advice, or a complete view of legal practice. It gives a researcher a first pass on public discourse and keeps enough context visible for checking.

### Where the evidence is

The README, `reflection.md`, `design.html`, and dashboard copy all describe the limits of the project. The evidence panels show source type and excerpts so a viewer can inspect the basis for a theme.

### What I learned

My judgment call was to make the limits visible instead of trying to make the tool sound more complete than it is. From law, I ask what supports the claim and what risk might be hidden. From UX research, I ask who needs the claim and what decision it helps them make. The useful part is the trace from theme, to excerpt, to source context, to product implication.

## C2 - Code Literacy and Documentation

### What I built

I packaged the project so someone else can understand it without asking me to explain every file. The README explains what the tool does, who it is for, how to run it, how live Reddit collection works, and where the public version is.

### Where the evidence is

The documentation is in `README.md`, `mp2.md`, `reflection.md`, `.env.template`, and the comments/docstrings inside the Python files. The notebook and generated CSVs also make the workflow easier to inspect.

### What I learned

The documentation had to answer the questions I would ask if I were opening someone else's project: what does it take in, what does it return, where can I see it, and what should I not overclaim? I wrote the README, reflection, and competency file around those questions.
