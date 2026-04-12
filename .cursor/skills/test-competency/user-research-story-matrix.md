# User research story verification matrix

This file defines the **verification system** used by the [test-competency](SKILL.md) skill. Agents classify each response (or distinct claim inside a long response) against these **user research story** types and score **evidence strength**.

## Story types (tags)

Use these tags to describe what kind of user narrative appears. A single response can have multiple tags.

| Tag | Definition | Look for |
|-----|------------|----------|
| `situation` | Context: where/when/how the user is working | Tools, team, phase of work, environment |
| `problem` | A concrete obstacle, tension, or failure mode | “Hard to…”, “bottleneck”, “doesn’t work” |
| `goal` | Desired outcome or success criteria | “I want…”, “we need…”, outcomes they chase |
| `workaround` | Informal fix, hack, or substitute behavior | “I started…”, “I use… instead”, shortcuts |
| `emotion` | Affective signal (stress, pride, frustration) | Emotional vocabulary, tone of burden |
| `stakeholder` | Other people/roles affecting the work | “Legal”, “engineers”, “nobody invites…” |
| `evidence-of-impact` | Effect on decisions, quality, or outcomes | What changed, killed, shipped, or measured |

## Evidence strength rubric

| Level | Criteria |
|-------|----------|
| **Strong** | First-person, specific situation, and at least one of: concrete example, named actor/artifact, consequence, or comparison |
| **Adequate** | Clear claim but thin context; reads like summary opinion without one vivid detail |
| **Weak** | Vague (“always”, “everyone”), purely hypothetical, or no verifiable situation |

## Pass/fail for “competency” of a single response

This is a **structured judgment**, not a grade on the participant.

- **Pass (rich narrative):** At least **two** story tags apply **and** evidence is **adequate** or **strong**.
- **Borderline:** One tag clearly applies and evidence is adequate.
- **Needs follow-up:** Weak evidence **or** only one thin tag—note what probe would help (e.g., “ask for a specific last time this happened”).

## Aggregate signals

When summarizing the whole corpus:

- **Coverage:** Which tags appear often vs rarely?
- **Risk:** Many `problem` + few `evidence-of-impact` → pain clear, outcomes unclear.
- **Triangulation:** Do `workaround` stories align with `goal` stories, or signal dysfunction?

Use this matrix consistently so verification results are comparable across sessions.
