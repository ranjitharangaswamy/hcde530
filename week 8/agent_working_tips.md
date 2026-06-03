Working With the Agent

Twelve habits for MP2 and beyond

HCDE 530  ·  SP26

01  Setting Up the Work

02  Working With the Agent

03  Catching Mistakes

1

Setting Up the Work

T I P   1
Convert source documents to markdown first

T I P   2
Keep your .cursorrules file alive

Before pasting a brief, transcript, or article into the agent, convert it
to .md. PDFs and Word docs carry formatting the agent doesn't need
and sometimes gets wrong. The markitdown tool handles most file
types in one command.

You wrote one in Week 2. Update it as MP2 takes shape — what
you're building, who it's for, what data it uses, what you've decided.
The agent reads it automatically every conversation.

T I P   3
Use .md files as standing instructions

T I P   4
Scope context with @

Keep a project_notes.md or decisions.md in your repo. Log what you
tried, what worked, what didn't. Reference it in prompts: "Read
project_notes.md first, then help me with X." This is how you give the
agent memory across sessions.

In Cursor, use @file, @folder, @codebase, and @docs to point the
agent at exactly what it should look at. Don't dump the whole repo
when you only need one file. Smaller, more specific context produces
sharper output.

2 Working With the Agent

T I P   5
Start fresh every 10–15 turns

T I P   6
Use Plan mode before edits

10–15 turns is a reasonable upper limit, but the real signal is
qualitative: when the agent starts repeating itself, contradicting earlier
decisions, or losing the thread — start fresh. Carry forward what
matters in your .md notes.

Ask the agent for a plan before it touches any files. Read the plan.
Push back on anything that looks wrong or overscoped. Approve only
what you understand. This is where you catch bad moves cheaply —
before they're in your files.

T I P   7
One change at a time

T I P   8
Explain before changing

Don't ask for three things in one prompt. The agent will do one well
and the others badly, and you won't be able to tell which is which
when you review the output. Sequence them.

Before asking the agent to modify a file, ask it to explain what the file
currently does. If the explanation is wrong, the change will be wrong.
A 30-second explanation step catches misunderstandings before they
become bugs.

3

Catching Mistakes

T I P   9
Read every diff

T I P   1 0
Commit before any big move

Cursor's accept-all button is a trap. Read each hunk. Accept hunks
individually. If you don't understand a hunk, ask the agent to explain it
before accepting — or reject it.

Before asking the agent to restructure, reorganize, or add a sizable
feature, commit your current state. If the big move goes sideways, you
have a clean version to return to and haven't lost an hour of work.

T I P   1 1
When the agent loops, stop it

T I P   1 2
Show, don't describe

If the agent has tried the same fix twice and failed, stop. Summarize
what you actually know — the error, what you've tried, what hasn't
worked — in your own words. Start a fresh conversation. Three
minutes of human framing beats twenty minutes of agent retries.

Paste the actual error message. Paste the actual file content. Paste the
actual output. The agent can't see your screen, and a description is
almost always less precise than the thing itself. Most stuck prompts
unstick the moment you paste the real artifact.

A few more things

If you use Claude Code:

The /context command is the equivalent of Cursor's @-based scoping — it limits what the agent reads to the files you point it at.

MCP servers:

MCP servers (e.g., Perplexity for web search inside the agent) exist and are worth knowing about. Look them up if you need them
for MP2 — they have setup overhead, so don't start one the night before a deadline.

MP2 submission — commit everything:

Your .cursorrules file, project_notes.md, and any other .md files belong in your GitHub repo. They show how you managed the
agent, not just what you built. Include them in your final commit.

HCDE 530  ·  Working With the Agent  ·  SP26

