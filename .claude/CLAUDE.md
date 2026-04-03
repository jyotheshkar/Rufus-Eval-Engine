# Rufus Eval Engine — Project Brain

## What this project is

A production-style LLM evaluation framework for an AI shopping assistant (Rufus).
It automatically judges the quality of AI-generated shopping answers using a second
LLM-as-a-judge pipeline, surfaces quality metrics in a dashboard, and runs adversarial
tests to expose failure modes.

This is a portfolio project built by Jyothesh Karnam targeting Language Engineer
and Applied ML roles at Amazon.

---

## The problem it solves

Rufus answers millions of shopping questions. How do you know if the answers are good?
- Is Rufus hallucinating product specs?
- Is it recommending the wrong products?
- Does quality drop on ambiguous or adversarial queries?

This system answers those questions automatically.

---

## Full system architecture

```
DATA LAYER          BACKEND (FastAPI)        FRONTEND (Next.js)
─────────────       ─────────────────        ──────────────────
products.json  -->  RAG retriever (FAISS) -> Overview screen
questions.json -->  Rufus agent (Haiku)   -> Answer feed
adversarial.json -> LLM judge (Haiku)    -> Weak spot analysis
eval_results.db <-- Anomaly detector     -> Adversarial report
```

## Backend pipeline (one eval run)

1. Load question from bank or adversarial suite
2. FAISS retrieves top-5 matching products
3. Rufus agent (Claude Haiku) generates shopping answer
4. LLM judge (Claude Haiku) scores on 4 dimensions
5. Anomaly detector flags drops vs rolling average
6. Save result to SQLite

---

## Evaluation dimensions

| Dimension     | What it measures                              | Score |
|---------------|-----------------------------------------------|-------|
| Helpfulness   | Did it answer what the customer actually asked? | 0-10  |
| Accuracy      | Are the product facts correct?                | 0-10  |
| Hallucination | Did it invent specs or features?              | 0-10  |
| Safety        | Did it mislead or pressure the customer?      | 0-10  |

---

## Project file structure

```
rufus-eval-engine/
├── .claude/
│   ├── CLAUDE.md                    # this file — project brain
│   ├── settings.json                # permissions, hooks, MCP, env
│   ├── settings.local.json          # personal overrides (gitignored)
│   ├── commands/
│   │   ├── phase1.md                # scaffold + data generation
│   │   ├── phase2.md                # FAISS vector store
│   │   ├── phase3.md                # Rufus agent
│   │   ├── phase4.md                # LLM judge pipeline
│   │   ├── phase5.md                # adversarial test suite
│   │   ├── phase6.md                # anomaly detection + SQLite
│   │   ├── phase7.md                # FastAPI backend
│   │   ├── phase8.md                # Next.js frontend
│   │   ├── phase9.md                # integration + deployment
│   │   └── document-phase.md        # slash command: generate phase docs
│   ├── agents/
│   │   ├── backend-agent.md         # Python/FastAPI specialist
│   │   └── frontend-agent.md        # Next.js/Tailwind specialist
│   ├── rules/
│   │   ├── code-style.md            # Python + TypeScript conventions
│   │   ├── testing.md               # pytest + Jest/RTL patterns
│   │   ├── api-conventions.md       # FastAPI routes, Pydantic, mock guard
│   │   ├── hooks.md                 # what hooks are configured and why
│   │   ├── plan-mode.md             # when to enter plan mode
│   │   ├── checkpoints.md           # phase gate criteria per phase
│   │   ├── mcp.md                   # MCP server config and usage
│   │   ├── plugins.md               # plugin guidelines
│   │   ├── compaction.md            # context compaction hints
│   │   ├── documentation.md         # documentation standards
│   │   └── tdd.md                   # TDD protocol
│   └── skills/
│       └── anatomy-of-sde/          # SDE scaffolding skill
├── backend/
│   ├── main.py
│   ├── agents/
│   │   ├── rufus_agent.py
│   │   └── judge_agent.py
│   ├── retrieval/
│   │   └── faiss_retriever.py
│   ├── evaluation/
│   │   ├── pipeline.py
│   │   └── anomaly.py
│   ├── data/
│   │   ├── products.json
│   │   ├── questions.json
│   │   ├── adversarial.json
│   │   ├── eval_results.db
│   │   └── mocks/
│   │       ├── mock_rufus.json
│   │       └── mock_judge.json
│   ├── scripts/
│   │   ├── generate_products.py
│   │   ├── generate_questions.py
│   │   └── run_eval.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── feed/page.tsx
│   │   ├── analysis/page.tsx
│   │   └── adversarial/page.tsx
│   ├── components/
│   │   ├── ScoreCard.tsx
│   │   ├── AnswerTable.tsx
│   │   ├── ScoreTrendChart.tsx
│   │   ├── CategoryBarChart.tsx
│   │   └── AnomalyBadge.tsx
│   ├── lib/
│   │   └── api.ts
│   └── __tests__/
├── docs/
│   ├── phase-1.md                   # auto-generated after phase 1 TDD
│   ├── phase-2.md                   # auto-generated after phase 2 TDD
│   └── ...
├── progress/
│   ├── phase-1-progress.md          # concise progress record after phase 1
│   ├── phase-2-progress.md          # concise progress record after phase 2
│   └── ...
├── README.md
└── .gitignore
```

---

## Tech stack

| Layer          | Technology                              |
|----------------|-----------------------------------------|
| Frontend       | Next.js 14, TypeScript, Tailwind CSS, Recharts |
| Backend        | Python 3.11, FastAPI, Pydantic          |
| Vector search  | FAISS                                   |
| LLM            | Claude Haiku (Anthropic API)            |
| Storage        | SQLite + JSON                           |
| Deployment     | Vercel (frontend), Railway (backend)    |

---

## CRITICAL RULES — never break these

### Budget protection (most important)
- NEVER call the Anthropic API in a loop during development
- ALWAYS use cached/mock responses during dev unless user says "run live"
- The entire project API budget is $10 maximum
- Mock response files live in backend/data/mocks/
- Claude Haiku pricing: input $0.80/1M tokens, output $4.00/1M tokens
- Estimate costs in the Unified Approval before any API-touching phase

### Code conventions — Python
- All FastAPI routes use async/await
- All models use Pydantic BaseModel
- All API calls wrapped in try/except with proper error responses
- Environment variables loaded via python-dotenv, never hardcoded
- Type hints on every function

### Code conventions — Next.js
- All components are TypeScript with proper interfaces
- Tailwind only — no custom CSS files
- All API calls go through lib/api.ts — never fetch directly in components
- Use Recharts for all charts — no other charting library

### Code conventions — General
- No console.log left in production code
- Every file gets a one-line comment at the top explaining what it does
- Keep functions small — one function, one job

---

## Standard Phase Workflow

This is the exact sequence for every phase. Follow it without deviation.

### Step 1 — Unified Pre-Phase Approval

When the user says "start phase X", output a **Phase X Execution Plan** block before
writing a single line of code. The block must contain:

```
## Phase X Execution Plan

### What will be built
- [file path] — [one-line purpose]
- [file path] — [one-line purpose]
...

### Commands that will run
- [command] — [why]
...

### API usage
- Yes / No
- If yes: estimated tokens (input + output), estimated cost in USD
- Mock guard status: USE_MOCK=true confirmed / WARNING: not set

### Phase command file
- .claude/commands/phaseX.md

### Rules files being applied
- .claude/rules/[relevant].md
```

After outputting the plan, ask: **"Approve this plan to proceed? Reply yes to start."**

Do not write any code, create any file, or run any command until the user replies yes.

### Step 2 — Execute (No Interruptions)

After approval:
- Run every step in the phase command file in order
- Do not stop for individual file write or Bash command approvals — settings.json already covers these
- If something fails, attempt to fix it autonomously — only stop if the failure is completely unrecoverable
- Report progress inline: "✓ Step 1/6 — folder structure created"

### Step 3 — TDD Gate

When all phase steps are complete, present a **TDD Plan** block:

```
## Phase X — TDD Plan

### Tests that will be written
| Test file | Function tested | Scenario | What passing proves |
|-----------|----------------|----------|---------------------|
| ...       | ...            | ...      | ...                 |

### Scalability checks
- [what this phase's code must handle as the project grows]

### Maintainability checks
- [what makes this code easy to change in future phases]
```

Ask: **"Approve TDD plan? Reply yes to run tests."**

After approval, write all tests and run them. If a test fails, fix the root cause —
do not skip or comment out the test.

### Step 4 — Documentation + Progress Record

After all tests pass, automatically (no approval needed):
1. Generate `docs/phase-X.md` following `.claude/rules/documentation.md`
2. Generate `progress/phase-X-progress.md` following `.claude/rules/phase-progress.md`

Both files are created before the Phase Complete Declaration.

### Step 5 — GitHub Push (requires permission)

After docs and progress are generated, ask for explicit push permission following
`.claude/rules/github-push.md`. Present the exact prompt defined in that rule and
wait for a yes/no reply. Do not push without a "yes".

### Step 6 — Phase Complete Declaration

State explicitly:
```
Phase X complete.
Built: [bullet list of what was built]
Tests: [N passed, 0 failed]
Docs: docs/phase-X.md generated
Progress: progress/phase-X-progress.md generated
GitHub: pushed / skipped (user chose not to push)
Next: say "start phase X+1" when ready
```

Do not start the next phase until the user explicitly says so.

---

## Phase overview

| Phase | What gets built                        |
|-------|----------------------------------------|
| 1     | Repo scaffold + data generation        |
| 2     | FAISS vector store + embeddings        |
| 3     | Rufus agent (shopping assistant)       |
| 4     | LLM judge pipeline (4 dimensions)      |
| 5     | Adversarial test suite                 |
| 6     | Anomaly detection + SQLite storage     |
| 7     | FastAPI backend (all endpoints)        |
| 8     | Next.js frontend (all 4 screens)       |
| 9     | Integration + deployment               |

---

## How to run phases

In Claude Code terminal, say:
- "start phase 2" → triggers Unified Approval → you approve → phase runs to completion
- "I need help with the backend" → reads agents/backend-agent.md
- "I need help with the frontend" → reads agents/frontend-agent.md
- `/document-phase 1` → regenerates docs/phase-1.md at any time

---

## Workflow

- All work happens on feature branches; merge to `main` only when a phase is complete
- A phase is only complete when: code written + TDD gate passed + docs generated
- Never push directly to `main` mid-phase
- Commit messages follow: `feat:`, `fix:`, `chore:`, `test:`, `docs:` prefixes
- Before starting a new phase, confirm the previous phase's checkpoint criteria are met (see `.claude/rules/checkpoints.md`)

---

## Features configured in this project

| Feature        | Location                             | Status        |
|----------------|--------------------------------------|---------------|
| Permissions    | `.claude/settings.json`              | Active        |
| Hooks          | `.claude/settings.json` + rules/hooks.md | Active    |
| Plan Mode      | `.claude/rules/plan-mode.md`         | Active        |
| Checkpoints    | `.claude/rules/checkpoints.md`       | Active        |
| MCP            | `.claude/settings.json` + rules/mcp.md | Phase 6+   |
| Plugins        | `.claude/rules/plugins.md`           | Phase 7+      |
| Context        | `.claude/rules/` (all files)         | Active        |
| Slash Commands | `.claude/commands/`                  | Active        |
| Compaction     | `.claude/rules/compaction.md`        | Active        |
| Subagents      | `.claude/agents/`                    | Active        |
| Documentation  | `.claude/rules/documentation.md`     | Active        |
| Phase Progress | `.claude/rules/phase-progress.md`    | Active        |
| GitHub Push    | `.claude/rules/github-push.md`       | Active        |
| TDD            | `.claude/rules/tdd.md`               | Active        |

---

## Rules

Detailed conventions live in `.claude/rules/` — read the relevant file before working in that area:

- `code-style.md` — Python and TypeScript naming, formatting, structure
- `testing.md` — pytest patterns for FastAPI, Jest/RTL for Next.js
- `api-conventions.md` — FastAPI routes, Pydantic models, mock guard
- `hooks.md` — budget protection and file write hooks
- `plan-mode.md` — when to enter plan mode before acting
- `checkpoints.md` — what must be true before a phase is marked complete
- `mcp.md` — SQLite MCP server, how and when to enable it
- `plugins.md` — eval-runner plugin pattern
- `compaction.md` — what to preserve when context is compressed
- `documentation.md` — how to write docs/phase-X.md files
- `phase-progress.md` — how to write progress/phase-X-progress.md files
- `github-push.md` — ask permission before pushing each completed phase to GitHub
- `tdd.md` — TDD protocol, test-first principles, scalability checks

---

## Context Compaction Hints

If this conversation is ever compacted, Claude must always preserve:
- **Current phase number and status** (in progress / complete)
- **USE_MOCK=true rule** — non-negotiable, budget protection
- **Remaining API budget** — total budget $10, track what has been spent
- **Phase completion checklist status** — which checkpoints have been verified
- **Any unresolved errors or blockers** from the current phase
- **The Standard Phase Workflow** — Unified Approval → Execute → TDD Gate → Docs → Complete

---

## Claude Instructions

- Always read the relevant `rules/` file before writing code in a new area
- Always check `USE_MOCK=true` is set before running any script that touches the Anthropic API
- Follow the Standard Phase Workflow exactly — no shortcuts
- If a test fails, fix the root cause — do not skip or comment out the test
- Documentation is not optional — generate docs/phase-X.md after every phase
