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
│   ├── CLAUDE.md                    # this file
│   ├── commands/
│   │   ├── phase1.md                # scaffold + data generation
│   │   ├── phase2.md                # FAISS vector store
│   │   ├── phase3.md                # Rufus agent
│   │   ├── phase4.md                # LLM judge pipeline
│   │   ├── phase5.md                # adversarial suite
│   │   ├── phase6.md                # anomaly detection + SQLite
│   │   ├── phase7.md                # FastAPI backend
│   │   ├── phase8.md                # Next.js frontend
│   │   └── phase9.md                # integration + deployment
│   └── agents/
│       ├── backend-agent.md         # Python/FastAPI specialist
│       └── frontend-agent.md        # Next.js/Tailwind specialist
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
│   │   └── eval_results.db
│   ├── scripts/
│   │   ├── generate_products.py
│   │   ├── generate_questions.py
│   │   └── run_eval.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # overview screen
│   │   ├── feed/page.tsx            # answer feed
│   │   ├── analysis/page.tsx        # weak spot analysis
│   │   └── adversarial/page.tsx     # adversarial report
│   ├── components/
│   │   ├── ScoreCard.tsx
│   │   ├── AnswerTable.tsx
│   │   ├── ScoreTrendChart.tsx
│   │   ├── CategoryBarChart.tsx
│   │   └── AnomalyBadge.tsx
│   ├── lib/
│   │   └── api.ts                   # all FastAPI calls
│   └── package.json
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

## Phase overview

| Phase | What gets built                        | Est. time  |
|-------|----------------------------------------|------------|
| 1     | Repo scaffold + data generation        | Day 1-2    |
| 2     | FAISS vector store + embeddings        | Day 3-4    |
| 3     | Rufus agent (shopping assistant)       | Day 5-6    |
| 4     | LLM judge pipeline (4 dimensions)      | Day 7-9    |
| 5     | Adversarial test suite                 | Day 10-11  |
| 6     | Anomaly detection + SQLite storage     | Day 12-13  |
| 7     | FastAPI backend (all endpoints)        | Day 14-16  |
| 8     | Next.js frontend (all 4 screens)       | Day 17-19  |
| 9     | Integration + deployment               | Day 20-21  |

---

## How to run phases

In Claude Code terminal, say:
- "start phase 1" → reads .claude/commands/phase1.md and builds
- "phase 1 done, start phase 2" → moves to next phase
- "I need help with the backend" → reads agents/backend-agent.md
- "I need help with the frontend" → reads agents/frontend-agent.md

---

## Workflow

- All work happens on feature branches; merge to `main` only when a phase is complete
- A phase is only complete when: code is written, tests pass, and the feature is manually verified
- Never push directly to `main` mid-phase
- Commit messages follow: `feat:`, `fix:`, `chore:`, `test:`, `docs:` prefixes
- Before starting a new phase, confirm the previous phase's criteria are met

---

## Rules

Detailed conventions live in `.claude/rules/` — read the relevant file before working in that area:

- `.claude/rules/code-style.md` — Python and TypeScript naming, formatting, and structure rules
- `.claude/rules/testing.md` — pytest patterns for FastAPI, Jest/RTL patterns for Next.js
- `.claude/rules/api-conventions.md` — FastAPI route structure, Pydantic models, response shapes, mock guard

---

## Claude Instructions

- Read the relevant `rules/` file before writing code in any new area
- Always check `USE_MOCK=true` is set before running any script that touches the Anthropic API
- When a phase is complete, say explicitly: "Phase X complete — [list what was built]"
- Do not start the next phase until the user says so
- Do not add features, refactor, or clean up code outside the current phase scope
- If a test fails, fix the root cause — do not skip or comment out the test
