# Phase Progress Documentation — Rufus Eval Engine

## Rule

After every phase is fully complete (code written + TDD gate passed + checkpoint verified),
generate a progress document in the `progress/` folder at the project root.

This is separate from `docs/phase-X.md`. The docs file is a technical deep-dive;
the progress file is a concise human-readable record of what happened.

---

## Where files go

```
progress/
  phase-1-progress.md
  phase-2-progress.md
  ...
```

The `progress/` folder lives at the project root (same level as `backend/`, `frontend/`, `docs/`).
Create it if it does not exist.

---

## progress/phase-X-progress.md structure

```markdown
# Phase X Progress — [Phase Name]
**Completed:** YYYY-MM-DD
**Phase status:** Complete

---

## What was done
[3-5 bullet points in plain English — what was built, what decisions were made]

## Files created or modified
| File | Change |
|------|--------|
| path/to/file.py | Created — [one-line purpose] |
| path/to/file.py | Modified — [what changed] |

## Test results
- Tests written: N
- Tests passed: N
- Tests failed: 0

## Checkpoint status
All checkpoint criteria met: Yes / No
[If No: list what is still outstanding]

## Issues encountered
[Any bugs hit, decisions revisited, or things that took longer than expected.
If none, write: None.]

## Notes for next phase
[Anything the next phase needs to know about what was built here.
If none, write: None.]
```

---

## Timing

- Generate `progress/phase-X-progress.md` immediately after `docs/phase-X.md` is generated
- Both happen automatically — no user approval needed
- The Phase Complete Declaration must include: `Progress: progress/phase-X-progress.md generated`

---

## Why this exists

The `docs/phase-X.md` files explain *what* was built for a technical reader.
The `progress/phase-X-progress.md` files record *what happened* during the phase —
blockers, test results, issues — for Jyothesh's own reference and for portfolio presentation.
