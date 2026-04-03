# /document-phase — Generate Phase Documentation

## Usage

```
/document-phase [phase number]
```

Examples:
- `/document-phase 1` — generate or regenerate docs/phase-1.md
- `/document-phase 2` — generate docs/phase-2.md

---

## What this command does

1. Reads the phase command file (`.claude/commands/phaseN.md`) to understand what was planned
2. Reads all files that were built in that phase (from the file structure in CLAUDE.md)
3. Reads the phase checkpoint results from `.claude/rules/checkpoints.md`
4. Reads any existing tests in `backend/tests/` or `frontend/__tests__/` for that phase
5. Generates `docs/phase-N.md` following the documentation standard in `.claude/rules/documentation.md`

---

## Documentation standard

The generated doc follows the structure in `.claude/rules/documentation.md`:

```
# Phase N — [Name]
Status / Date / Built by

## What this phase built        ← plain English, 2-3 sentences
## Why this phase matters       ← connects to the bigger picture
## What was built               ← one section per file/component
## How data flows               ← step-by-step, no jargon
## Tests written                ← table of tests and what they prove
## Checkpoint verification      ← checklist with pass/fail
## Known limitations            ← honest assessment
## What comes next              ← one sentence bridge to next phase
```

---

## Writing standard

- Plain English — a non-technical person should be able to understand it
- No assumed knowledge — explain every technical term the first time it appears
- Short paragraphs — 3-4 sentences max
- 400-800 words total (not counting tables and code blocks)

---

## When this runs automatically

This command is invoked automatically at the end of every phase after the TDD gate passes.
You do not need to run it manually unless you want to regenerate a doc.

---

## Output

Creates or overwrites `docs/phase-N.md` in the project root.
Confirms: "docs/phase-N.md generated."
