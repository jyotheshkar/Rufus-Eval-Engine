# GitHub Push Rule — Rufus Eval Engine

## Rule

After a phase is fully complete, Claude must ask for explicit permission before
pushing anything to GitHub. Claude will never push automatically.

---

## When this triggers

At the end of every phase, after:
- All code is written
- TDD gate has passed (all tests green)
- `docs/phase-X.md` has been generated
- `progress/phase-X-progress.md` has been generated
- All checkpoint criteria are verified

Claude must present the following prompt and wait for a yes/no response:

```
Phase X is complete. Ready to push to GitHub.

This will:
  1. Stage all changed and new files for phase X
  2. Commit with message: "feat: phase X complete — [phase name]"
  3. Push to the `main` branch on GitHub

Do you want me to push phase X to GitHub? Reply yes to push, or no to skip.
```

Do not push until the user explicitly replies "yes". If the user says "no" or does not
respond, skip the push — the user can push manually at any time.

---

## Commit message format

```
feat: phase X complete — [phase name]

- [bullet: key thing built]
- [bullet: key thing built]
- [bullet: key thing built]

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

## Files to stage

Stage all files that belong to the phase:
- New and modified files in `backend/`, `frontend/`, `docs/`, `progress/`
- New or modified `.claude/` files
- Do NOT stage: `.env`, `*.secret`, `backend/data/eval_results.db`, `__pycache__/`, `node_modules/`

---

## Branch policy

- Push to `main` — phases are complete, stable units of work
- Never push mid-phase to `main`
- If the user is on a feature branch, push to that branch instead and note it

---

## After pushing

Confirm with:
```
Pushed phase X to GitHub.
Branch: main
Commit: [short hash] feat: phase X complete — [phase name]
```

If the push fails (e.g., remote has diverged), report the error and ask the user
how to proceed. Do not force-push without explicit instruction.
