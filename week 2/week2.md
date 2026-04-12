# Week 2 — Competency 2: Code literacy & documentation
```
## What Competency 2 means to me

**Documentation (my working definition):** Documentation is a form of *context-engineering* files with clear instructions on what project I am working on, what fixes to implement, and what output is expected. It facilitates creation of structures, interpretable artifactrs that describe a problem clearly, along with its constraints, decisions, and expected outcomes. This makes it easy for collaborators, users, distributors, and any third party who has access to follow the code easily and ensure that the computational tools are made with clarity and alignment.

**Code literacy:** Code literacy is the ability to read, interpret, and critically evaluate code as a form of argument and infrastructure. It includes understanding how logic, data structures, and abstractions produce outcomes, as well as being able to modify or write small scripts to test ideas, surface assumptions, and support research workflows.

```
## What I did this week
1. Wrote and refined small scripts to clean and transform sample CSV data for analysis
2. Reviewed and edited project documentation files (e.g., context.md, .cursorrules) to better define task scope and expected outputs
3. Iterated and created a dashboard prototype for user research, focusing on how data is surfaced and interpreted
4. Made incremental commits documenting changes to both code and structure
5. Tested workflows that integrate documentation with tool-assisted coding environments

—

## Observations — code literacy
As a lawyer transitioning into HCDE, this week reinforced that reading code is often more important than writing it. I found myself tracing logic step-by-step to understand how outputs were being generated, which mirrors how I read legal texts with attention to structure and implication. Writing small scripts felt less like “programming” and more like constructing procedural arguments.
A key growth area is building confidence in modifying existing code rather than defaulting to rewriting from scratch.
Drawing from the class pre-readings, particularly, the piece by Nate's youtube video, I’m starting to see code not just as execution, but as a medium for shaping systems of action. 

—

## Observations — documentation
I approached documentation as an active design layer. In files like context.md, I articulated the “why” behind tasks, the constraints shaping decisions, and the form of acceptable outputs. This made it easier to re-enter the project after breaks and reduced ambiguity when switching between tools.

What was most useful was specifying expectations clearly enough that both I (later) and the system or Cursor (now) could follow them without reinterpretation. What was challenging was deciding the right level of detail; if it's too vague, it becomes unhelpful, if it is too rigid, it limits iteration.

This aligns with a legal mindset that documentation functions like a brief or a contract. It anticipates interpretation and tries to reduce misalignment before it happens.
—

## Connection to design / research practice
1. Connects to UX research in qualitative analysis, particularly in writing scripts to transform data parallels, cleaning and structuring research findings.
2. Building dashboards reflects decisions about what insights are visible and actionable.
3. It translates messy, evolving information into a shared understanding that others can act on.
4. This week emphasized that technical systems are also social systems. We need to define structures, give context or build a system that is efficient, but also provides equitable access to whoever wants to contribute or use it.   

—

## One thing I want to get better at next
1. I want to improve my ability to read and modify unfamiliar codebases.
2. I want to refine my code more efficiently, ship even faster. 
—

## Notes / quotes / links

*(Optional: syllabus lines, feedback, or resources.)*
*“Clarity scales; ambiguity compounds.”– Nate's Youtube video and substack
*Treat documentation as infrastructure, not an afterthought
Good context reduces the need for constant intervention

—

## Test competency (Week 2 response check)

This section applies the project **test-competency** skill: a repeatable way to check qualitative **responses** against a user-research **story** rubric, then summarize who the users sound like and what they need end-to-end.

### What the skill is

- **Where it lives:** `.cursor/skills/test-competency/SKILL.md` (with the verification matrix in `user-research-story-matrix.md`).
- **What it does:** (1) tags each quote with story types (e.g. situation, problem, workaround, stakeholder), (2) scores **evidence strength** (strong / adequate / weak), (3) builds one **synthetic persona** from patterns across the set, and (4) draws a **user journey map** so needs stay explicit—not jump straight to solutions.

### Data for this week

- **Source:** `demo_responses.csv` (synthetic UX practitioner interviews: **25** rows, columns `participant_id`, `role`, `response`).
- **Why this matches Week 2:** the coursework thread is code + documentation + surfacing research data; this corpus stands in for “messy qualitative input” the same scripts and dashboard interpret.

### Verification summary (user research stories)

Tags are from the matrix: `situation`, `problem`, `goal`, `workaround`, `emotion`, `stakeholder`, `evidence-of-impact`.

| Signal | What we see in the 25 responses |
|--------|----------------------------------|
| **Coverage** | Almost every response combines **situation** (how people work) + **problem** (bottleneck or tension). **Stakeholder** conflict appears often (engineering, legal, leadership). **Workaround** shows up repeatedly (hallway tests, shorter briefs, async synthesis, confidence ratings). |
| **Evidence strength** | The majority read as **strong**: first-person, concrete scenes (e.g. diary study vs. claimed behavior, killing features, onboarding with no owner). A few lean **adequate** when the claim is broad (“always,” “nobody”) but still anchored in role context. |
| **Risk pattern** | Many **problem** + **emotion** (frustration) stories; **evidence-of-impact** is present but uneven—several people describe decisions *not* changing, which is itself a finding. |
| **Competency bar** | Under the skill’s rule (*≥2 tags* and adequate+ evidence), **most rows pass** as rich narratives; borderline cases tend to be shortest or most generic—where you’d add a follow-up probe for a specific instance. |

*Illustrative row checks (abbreviated):*

| ID | Tags (sample) | Strength | Note |
|----|----------------|----------|------|
| P02 | problem, stakeholder, workaround, emotion | Strong | “Framing research as risk reduction” = workaround + stakeholder bridge |
| P08 | problem, stakeholder, emotion | Strong | Findings vs. decisions gap—outcome is organizational |
| P13 | situation, problem, evidence-of-impact | Strong | Concrete contradiction (diary vs. self-report) |
| P20 | evidence-of-impact, goal | Strong | Features killed—rare clear impact story |
| P22 | problem, stakeholder, situation | Strong | Ownership gap across functions |

### Sample persona (synthetic — from this week’s corpus)

**Alex Chen — mid-career cross-functional UX role (blend of researcher, designer, PM voices)**  
People in this sample are trying to **run credible research inside fast product cycles**, **bring others along**, and **see work land in decisions**—not only in decks.

- **Goals:** protect time for discovery; get findings into decisions; reduce recruiting and synthesis drag; improve clarity for users (language, a11y, errors).
- **Frustrations:** research squeezed late; low documentation upstream; power dynamics (“senior already knows”); synthesis fatigue; tools/process that don’t match urgency.
- **Behaviors (data-grounded):** reframing research as risk reduction; hallway tests; shorter readouts; confidence ratings; async boards; AI-assisted transcripts with human pass; pushing terminology and error copy earlier.
- **Quote anchors:** P04 recruiting bottleneck; P08 findings not changing decisions; P14 reports nobody reads; P20 killing features from research.

### User journey map (needs-focused)

| Stage | User actions / context | Needs (explicit) | Pain points | Opportunities |
|-------|-------------------------|------------------|-------------|----------------|
| **Frame the problem** | Read vague briefs; interview stakeholders to learn what the product is | Understand real goals and constraints; avoid building the wrong thing | Missing docs; unclear product intent | Lightweight stakeholder alignment rituals; clearer problem statements |
| **Plan research** | Fight for calendar time; recruit; choose methods | Get participants; secure time in the plan; match method to risk | Recruiting bottleneck; time boxed to sprint start | Panels; standing research slots; method matched to decision risk |
| **Execute** | Run sessions; balance rigor and speed | Listen well; capture usable signal; avoid bias | Steering vs. listening; covering too many topics | Session discipline; paired moderators or scripts |
| **Synthesize** | Affinity mapping; async Miro; AI assist | Turn data into themes the team will use | Participation drops; report writing eats time | Shorter briefs; async norms; AI + human nuance pass |
| **Influence decisions** | Present decks; push back on seniors; tie to roadmaps | Translate findings into choices; protect users when patterns misfit | Nods then business as usual; design system as crutch | Confidence labels; traceability to decisions; exec-ready short forms |
| **Ship & learn** | Handoffs for IA, content, errors; longitudinal studies when possible | Same vocabulary; accessible behavior; learn over time | Siloed ownership; legal vs. plain language; no longitudinal budget | Terminology audits; early a11y sessions; diary studies when stakes warrant |

**Key moments (needs peak):** (1) **Recruiting / scope** — can’t learn without people and focus. (2) **Synthesis participation** — insight dies if the team won’t engage. (3) **Decision meeting** — research meets power and habit. (4) **Handoff to UI/content** — language and errors become user reality. (5) **Proof of impact** — without examples like killing a feature, value stays rhetorical.

---

*This appendix documents how Week 2’s qualitative “response” set was checked with **test-competency**; regenerate or extend if `demo_responses.csv` changes.*
