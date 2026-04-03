# Phase 7 — FastAPI Backend (All Endpoints)

## Goal
Build the full REST API that the Next.js frontend will call.
All endpoints read from SQLite. No LLM calls happen via the API —
evals are run via scripts, not triggered by the frontend.

---

## Step 1 — Build main.py

File: `backend/main.py`

```python
# Entry point for the Rufus Eval Engine FastAPI application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import evals, stats, adversarial

app = FastAPI(title="Rufus Eval Engine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-url.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evals.router)
app.include_router(stats.router)
app.include_router(adversarial.router)
```

---

## Step 2 — Build all endpoints

Use `APIRouter` — one file per domain. Mount all routers in `main.py`.

### GET /health
```json
{"status": "ok", "total_evals": 200, "last_run": "2025-03-15T14:22:00Z"}
```

### GET /evals
Paginated list. Query params: `page`, `limit`, `category`, `difficulty`, `is_adversarial`, `min_score`, `max_score`
```json
{"total": 200, "page": 1, "results": [...]}
```

### GET /evals/{eval_id}
Single eval result with full detail.

### GET /stats/overview
Dashboard KPIs:
```json
{
  "total_evals": 200,
  "avg_overall": 7.4,
  "avg_helpfulness": 7.8,
  "avg_accuracy": 7.6,
  "avg_hallucination": 8.1,
  "avg_safety": 8.9,
  "anomaly_count": 12,
  "worst_category": "price_trap"
}
```

### GET /stats/by-category
```json
[
  {"category": "headphones", "avg_overall": 7.9, "count": 45},
  {"category": "laptops", "avg_overall": 7.2, "count": 38}
]
```

### GET /stats/trend
Query param: `days` (default 7)
```json
[
  {"date": "2025-03-10", "avg_overall": 7.1},
  {"date": "2025-03-11", "avg_overall": 7.4}
]
```

### GET /stats/anomalies
```json
[
  {
    "eval_id": "...",
    "timestamp": "...",
    "question": "...",
    "score_overall": 3.2,
    "anomaly_reason": "Score 2.1 std devs below category mean"
  }
]
```

### GET /adversarial/summary
Adversarial results summary by failure mode.

---

## Step 3 — Build eval-runner plugin

Create `.claude/skills/eval-runner/SKILL.md` — see `.claude/rules/plugins.md` for the spec.
This plugin lets you trigger a single eval run for debugging during this phase.

---

## Step 4 — Run and test locally

```bash
uvicorn backend.main:app --reload --port 8000
```

Verify:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/stats/overview
curl "http://localhost:8000/evals?page=1&limit=10"
```

---

## Phase 7 complete when:
- All 8 endpoints implemented and returning correct shapes
- CORS configured for `localhost:3000`
- API docs auto-generated at `http://localhost:8000/docs`
- All endpoints handle empty DB gracefully (return empty arrays, not errors)
- Every route has a happy-path test and an error test
- eval-runner plugin created
- Tests pass
- `docs/phase-7.md` generated
