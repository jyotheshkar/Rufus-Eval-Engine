# Documentation — Rufus Eval Engine

## Purpose

Every phase produces a `docs/phase-X.md` file automatically after the TDD gate passes.
These docs serve three purposes:

1. **For Jyothesh** — a clear record of what was built, so you can re-read any phase
   and immediately understand what exists and why
2. **For anyone else** — written in plain English with no assumed knowledge, so a
   non-technical reader can understand what the system does
3. **As compaction backup** — Claude can re-read these files after context compression
   to restore full project understanding without needing the original conversation

---

## Documentation standard: write for a smart non-engineer

Imagine a smart person who has never written code reading your doc.
They should be able to understand:
- What was built in this phase
- Why it was built
- How it fits into the bigger picture
- What the inputs and outputs are
- What tests were written and what they proved

Avoid jargon. When you must use a technical term, explain it in plain English the first time.

**Bad:** "FAISS uses an IVF index with L2 distance for ANN retrieval"
**Good:** "We built a search engine that finds the 5 most relevant products for any shopping
question. It works by converting every product into a list of numbers (called an embedding)
that captures its meaning, then finding the products whose numbers are closest to the
question's numbers."

---

## docs/phase-X.md structure

Every phase doc must follow this exact structure:

```markdown
# Phase X — [Phase Name]
**Status:** Complete
**Date completed:** YYYY-MM-DD
**Built by:** Claude (claude-haiku model) + Jyothesh Karnam

---

## What this phase built

[2-3 sentences in plain English. What exists now that didn't before?]

---

## Why this phase matters

[1-2 sentences. How does this phase enable the next one? What problem does it solve?]

---

## What was built

### [Component name]
**File:** `path/to/file.py`
**What it does:** [Plain English explanation — one paragraph max]
**Key decisions made:**
- [Decision and why]

[Repeat for each component/file built in this phase]

---

## How data flows through this phase

[A step-by-step description in plain English of how data moves through what was built.
Use numbered steps. No code unless absolutely necessary.]

---

## Tests written

| Test | What it checks | Why it matters |
|------|---------------|----------------|
| [test name] | [plain English] | [why this matters for the project] |

---

## Checkpoint verification

[Copy the phase checklist from rules/checkpoints.md and mark each item ✓ or ✗ with a note]

---

## Known limitations

[Anything that works but has a known shortcoming. If none, write: "None identified."]

---

## What comes next

[One sentence about what Phase X+1 will build on top of this.]
```

---

## Tone and length guidelines

- Use short paragraphs (3-4 sentences max)
- Use bullet points for lists of 3+ items
- Use tables for structured comparisons
- Total length: 400–800 words (not counting code blocks or tables)
- No filler phrases like "In this phase, we..." — just state the fact directly

---

## Slash command

Run `/document-phase N` at any time to regenerate `docs/phase-N.md`.
See `.claude/commands/document-phase.md` for the full command definition.
