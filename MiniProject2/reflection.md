# Reflection: DocketSignal

## What did I build?

I built DocketSignal, a small research pipeline and static dashboard for looking at public Reddit discourse about legal AI. The tool collects or loads posts and comments, cleans the text, assigns early qualitative themes, adds sentiment and rhetorical-frame tags, and turns the results into CSV files, excerpts, memos, charts, and a public-facing dashboard.

The audience I had in mind was a legal-tech researcher, UX researcher, or product collaborator who wants to understand what people are publicly worried about. The main issues that surfaced were hallucinated citations, trust, billing pressure, adoption resistance, governance, workflow gains, role anxiety, and tool comparison. I wanted the project to feel like an early research readout, where someone can start with the theme ranking and then check the excerpts that support it.

There are two layers to the final artifact. The Python layer creates the research material. The website layer explains it. I also built design thinking, competency, and reflection pages because the project needed to show more than the dashboard. It needed to show why I made the choices I made.

## What decisions did I make?

I chose a Cursor + Python project because the hard part of this project was the data and analysis pipeline. A full web app would have been more work than the project needed. A static dashboard was enough to make the work visible, especially for the MP2 gallery.

I kept Reddit as the live data source because it has public discussion from lawyers, law students, legal-tech users, and adjacent professionals. It also has an official API path through PRAW, which made it easier to stay inside a clear data boundary. I dropped broader web scraping and LinkedIn-style collection because those sources would have raised more provenance and terms-of-service issues. For this version, I wanted a smaller scope that I could explain honestly.

I also made a design decision around the evidence panels. A frequency chart can show which themes appear most often, but it does not show how different arguments feel. A concern about fake citations reads differently from a billing concern or a junior-lawyer anxiety concern. That is why the design thinking page explains the visual choices by theme. I used legal reasoning to keep evidence and source context visible. I used UX research thinking to make the themes easier to scan, compare, and question.

## What would I do differently?

I would add a human validation loop inside the tool. Right now the theme labels are transparent, and the excerpts are inspectable, but the actual validation still happens outside the interface. A stronger version would let the researcher accept, reject, rename, or merge codes in the dashboard. Then the tool could export a revised codebook and a revised corpus.

I would also preserve collection runs instead of overwriting the same output files. If I ran the Reddit collector every week, I would want each run to keep its own timestamp, query terms, subreddit list, and row counts. That would make it easier to compare how the conversation changes over time.

The design system is another place I would test more. I made a case that different discourse types deserve different evidence layouts. I still think that is a useful idea, but I would want to test it with legal researchers. Some users may want a dense uniform view when they are doing repeated analysis. A later version could have a showcase mode and a review mode.

## What does this work demonstrate?

This project demonstrates computational fluency, data ethics, qualitative research judgment, communication design, and design thinking across disciplines. The computational part is visible in `src/pipeline.py`, `src/collect_reddit.py`, and `src/qualitative.py`. Those files collect, clean, code, summarize, and export the corpus.

The data ethics part is visible in the Reddit-only scope, `.env.template`, source provenance, and the repeated boundary that DocketSignal is a research support tool. The qualitative research part is visible in the theme summaries, illustrative excerpts, and memos. The interface design part is visible in the way the dashboard moves from counts to evidence to product implications.

The cross-discipline piece is important to me. This project let me connect legal training with UX research. From law, I brought attention to evidence, risk, confidentiality, citations, billing, and governance. From UX research, I brought coding, synthesis, stakeholder framing, and interface decisions. DocketSignal shows how those habits can work together in a product research artifact.
