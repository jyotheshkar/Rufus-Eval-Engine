# Plan Mode — Rufus Eval Engine

## What is plan mode

Plan mode forces Claude to write out a full implementation plan and get explicit approval
before making any changes to the codebase. No files are written, no commands are run —
only a plan is produced and reviewed.

In Claude Code, enter plan mode by pressing **Shift+Tab** or typing `/plan` before describing a task.

---

## When to use plan mode in this project

Plan mode is required before any of the following actions. Do not start these without it.

### Architecture decisions
- Choosing the FAISS index type (Flat vs IVF vs HNSW) in Phase 2
- Designing the judge prompt structure in Phase 4
- Designing the anomaly detection algorithm in Phase 6
- Designing the SQLite schema in Phase 6

### High-risk modifications
- Any change to `backend/evaluation/pipeline.py` after Phase 4 (it is the core)
- Any change to the Pydantic model shapes in `backend/models.py`
- Any change to `frontend/lib/api.ts` (breaks all frontend components)

### Phase transitions
- Before starting Phase 7 (FastAPI) — plan the full endpoint surface
- Before starting Phase 8 (frontend) — plan the component tree and data flow
- Before starting Phase 9 (deployment) — plan the environment variable strategy

### Cross-cutting changes
- Adding a new field to `EvalResult` (cascades through DB schema, API, and frontend)
- Changing the scoring scale (e.g., 0-10 to 0-100)
- Changing the database path or name

---

## What a good plan looks like

A plan must answer:
1. **What** — exact files that will be created or modified
2. **Why** — the reasoning behind each decision
3. **How** — the specific approach (e.g., which FAISS index, why)
4. **Risk** — what could go wrong and how it is mitigated
5. **Rollback** — how to undo the change if it breaks something

---

## What is NOT required for plan mode

Routine operations that do not require plan mode:
- Adding a new test to an existing test file
- Adding a new question to `questions.json`
- Updating a comment or docstring
- Adding a new route that follows an identical pattern to an existing one
- Fixing a bug where the fix is obvious and localised

---

## Plan mode and the Unified Approval

Plan mode is different from the Unified Approval at the start of each phase:
- **Unified Approval** = approval for an entire phase's worth of work (happens once per phase)
- **Plan mode** = approval for a specific architectural decision within a phase

You can use both. For a complex phase, enter plan mode for the architecture decision,
then get Unified Approval for the full phase execution.
