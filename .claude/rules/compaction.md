# Compaction — Rufus Eval Engine

## What is context compaction

As a conversation grows across a long multi-phase project, Claude's context window fills up.
Claude Code automatically compresses earlier parts of the conversation into a compact summary
so the session can continue. This is called compaction.

The risk: important project rules, budget constraints, and phase status can get lost in
a poor summary. This file tells Claude exactly what must survive every compaction.

---

## What must always be preserved

When this conversation is compacted, the summary MUST include all of the following.
If any item is missing from the compacted context, restate it before continuing work.

### 1. Current phase and status
```
Current phase: [number]
Status: [in_progress / tdd_gate / complete]
Last verified checkpoint: [phase N checkpoint passed/failed]
```

### 2. Budget status (non-negotiable)
```
API budget: $10.00 total
Spent so far: $[amount]
Remaining: $[amount]
USE_MOCK rule: ALWAYS true unless user says "run live"
```

### 3. Active blockers or errors
```
Any unresolved errors from the current phase that have not been fixed.
Any test failures that have not been addressed.
```

### 4. Phase completion status
A one-line status for each completed phase:
```
Phase 1: complete — products(1000), questions(200), adversarial(50), docs generated
Phase 2: complete — FAISS index built, embeddings in products.json, docs generated
Phase 3: [status]
...
```

### 5. The Standard Phase Workflow (condensed)
```
Workflow: Unified Approval → Execute (no interruptions) → TDD Gate → Docs → Phase Complete
```

### 6. Critical rules (always restate these)
```
- Never call Anthropic API without USE_MOCK=true check
- Never push to main mid-phase
- Never skip failing tests
- Always generate docs/phase-X.md after TDD gate passes
```

---

## What does NOT need to survive compaction

- Individual file contents (Claude can re-read them)
- Git history (Claude can run git log)
- Detailed step-by-step logs of completed work (the docs/ files capture this)
- Conversation pleasantries

---

## How to use this file

This file is not something you invoke — it is a standing instruction to Claude.
Every time Claude Code compacts this conversation, it uses this file to know what
to prioritise in the summary.

If you ever feel Claude has "forgotten" something important after a long session,
ask: "check compaction.md and restate current status." Claude will re-read this
file and confirm the critical state.

---

## Docs as a compaction backup

The `docs/phase-X.md` files serve as a durable record of everything that was built
in each phase. Even if compaction loses detail, Claude can re-read `docs/phase-1.md`
to fully understand what was built in Phase 1 without needing the original conversation.

This is why documentation is mandatory — it is the compaction safety net.
