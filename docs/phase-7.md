# Phase 7 — FastAPI Backend (All Endpoints)
**Status:** Complete
**Date completed:** 2026-04-03
**Built by:** Claude (claude-sonnet-4-6) + Jyothesh Karnam

---

## What this phase built

A complete REST API that exposes all eval data stored in SQLite as JSON endpoints for the Next.js dashboard. Eight endpoints cover everything the frontend needs: paginated eval results, dashboard KPIs, category breakdowns, score trends, anomaly lists, and adversarial failure summaries. All read from the database — no LLM calls happen via the API.

---

## Why this phase matters

The pipeline (phases 2–6) produces data; the frontend (phase 8) displays it. This API is the bridge between them. Without it, the dashboard has nothing to read. Getting the response shapes right here means phase 8 can be built purely against these contracts.

---

## What was built

### Pydantic models
**File:** `backend/models.py`
**What it does:** Defines typed response shapes for every endpoint using Pydantic BaseModel. All fields have `Field()` descriptions which auto-generate the OpenAPI docs at `/docs`. SQLite INTEGER booleans (`anomaly_flagged`, `is_adversarial`) are surfaced as Python `bool`.

| Model | Used by |
|-------|---------|
| `HealthResponse` | GET /health |
| `EvalResult` | GET /evals, GET /evals/{id} |
| `EvalListResponse` | GET /evals |
| `OverviewStats` | GET /stats/overview |
| `CategoryStat` | GET /stats/by-category |
| `TrendPoint` | GET /stats/trend |
| `AnomalyItem` | GET /stats/anomalies |
| `AdversarialCategoryStat` | GET /adversarial/summary |
| `AdversarialSummary` | GET /adversarial/summary |

### evals router
**File:** `backend/routes/evals.py`
**Endpoints:**
- `GET /evals` — paginated list with optional filters: `page`, `limit`, `category`, `is_adversarial`. Returns `EvalListResponse`. Empty DB returns `total=0, results=[]`.
- `GET /evals/{eval_id}` — single result by ID. Returns 404 with detail message if not found.

### stats router
**File:** `backend/routes/stats.py`
**Endpoints:**
- `GET /health` — status check with total eval count and last run timestamp
- `GET /stats/overview` — dashboard KPIs: averages across all 4 dimensions, anomaly count, worst adversarial category
- `GET /stats/by-category` — per-category averages sorted by overall score descending
- `GET /stats/trend` — daily average overall score for the last N days (default 7)
- `GET /stats/anomalies` — list of flagged anomalies ordered by timestamp descending

### adversarial router
**File:** `backend/routes/adversarial.py`
**Endpoints:**
- `GET /adversarial/summary` — aggregated failure stats by category: count, triggered count, failure rate, avg overall score

### FastAPI app
**File:** `backend/main.py`
**What it does:** Creates the FastAPI application, configures CORS for `http://localhost:3000`, mounts all three routers, and sets up logging. Auto-generates interactive API docs at `/docs`.

### eval-runner plugin
**File:** `.claude/skills/eval-runner/SKILL.md`
**What it does:** Documents the eval-runner skill so it can be invoked to run a single question through the pipeline during debugging without leaving Claude Code.

---

## How data flows through this phase

1. Frontend (or curl) makes a request to e.g. `GET /stats/overview`
2. FastAPI routes the request to the correct handler in the appropriate router
3. Handler opens an aiosqlite connection to `eval_results.db`
4. SQL query aggregates the data (AVG, COUNT, GROUP BY, etc.)
5. Result rows are mapped to Pydantic model instances
6. FastAPI serialises the model to JSON and returns it with HTTP 200
7. Empty DB queries return sensible defaults (0s, empty lists) — never 500 errors

---

## Tests written

| Test | What it checks | Why it matters |
|------|---------------|----------------|
| `test_health_returns_ok` | GET /health → 200, status="ok" | Liveness check for deployment |
| `test_evals_returns_list` | GET /evals → correct shape | Frontend eval feed depends on this |
| `test_evals_pagination` | page=2 returns different/empty results | Pagination contract |
| `test_eval_by_id_found` | GET /evals/{valid_id} → 200 | Detail view navigation |
| `test_eval_by_id_not_found` | GET /evals/{bad_id} → 404 | Error handling contract |
| `test_stats_overview_keys` | All required keys present | Dashboard KPI widget |
| `test_stats_by_category_is_list` | Returns list | Category bar chart |
| `test_stats_trend_is_list` | Returns list | Score trend chart |
| `test_stats_anomalies_is_list` | Returns list | Anomaly badge count |
| `test_adversarial_summary_shape` | total field present | Adversarial report screen |
| Empty DB tests (×all endpoints) | No 500 on empty DB | Graceful cold-start |

**Total: 19 passed, 0 failed**

---

## Checkpoint verification

- ✓ All 8 endpoints implemented and returning correct shapes
- ✓ CORS configured for `localhost:3000`
- ✓ API docs auto-generated at `/docs`
- ✓ All endpoints handle empty DB gracefully
- ✓ Every route has happy-path and error tests
- ✓ eval-runner plugin created
- ✓ `docs/phase-7.md` generated

---

## Known limitations

The `/stats/trend` endpoint groups by date string from the timestamp ISO field. In SQLite this works correctly for UTC timestamps. If the DB ever stores mixed timezones the grouping may produce duplicates — not a concern for this project.

---

## What comes next

Phase 8 builds the Next.js frontend — four screens that call this API to display the eval dashboard, answer feed, category analysis, and adversarial report.
