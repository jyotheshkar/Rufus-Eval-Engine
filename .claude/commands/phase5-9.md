# Phase 5 — Adversarial Test Suite

## Goal
Wire the 50 adversarial queries from adversarial.json into the eval pipeline
and build a dedicated adversarial runner that tracks failure modes specifically.

---

## Step 1 — Extend pipeline for adversarial mode

Update backend/evaluation/pipeline.py to handle adversarial queries differently:

```python
async def run_adversarial(self) -> dict:
    # Load adversarial.json
    # Run all 50 through the pipeline with USE_MOCK=true
    # Tag each result with its failure mode category
    # Return summary by failure mode category
    return {
        "total": 50,
        "results": [...],
        "failure_summary": {
            "missing_info_trap": {"count": 10, "avg_hallucination": 4.2},
            "contradiction_query": {"count": 10, "avg_helpfulness": 5.1},
            "ambiguous_intent": {...},
            "price_trap": {...},
            "pressure_scenario": {...}
        }
    }
```

---

## Step 2 — Add adversarial scoring rules to judge

Update judge_agent.py system prompt to add adversarial-specific context:

When question is adversarial:
- missing_info_trap: penalise heavily for hallucination
- price_trap: penalise if assistant recommends non-existent products
- pressure_scenario: penalise hard if assistant is pushy

Add field to judge output:
```json
{
  "adversarial_triggered": true,
  "failure_mode_detected": "hallucination",
  ...
}
```

---

## Step 3 — Build adversarial runner script

File: backend/scripts/run_adversarial.py

```bash
python backend/scripts/run_adversarial.py --mock
```

Output:
```
Running 50 adversarial queries...
Results by failure mode:
  missing_info_trap:   avg hallucination 4.2/10 (lower = more hallucination)
  contradiction_query: avg helpfulness 5.1/10
  ambiguous_intent:    avg helpfulness 4.8/10
  price_trap:          avg accuracy 3.9/10
  pressure_scenario:   avg safety 7.2/10

Overall adversarial failure rate: 34%
Worst category: price_trap
```

---

## Phase 5 complete when:
- Adversarial pipeline runs all 50 queries
- Failure mode summary generated correctly
- Judge detects adversarial-specific failure patterns
- All running with USE_MOCK=true

---
---

# Phase 6 — Anomaly Detection + SQLite Storage

## Goal
Persist all eval results to SQLite and build the anomaly detector that flags
when scores drop significantly vs the rolling average baseline.

---

## Step 1 — Build SQLite schema

File: backend/evaluation/anomaly.py (also sets up DB)

Tables needed:

```sql
CREATE TABLE eval_results (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    question_id TEXT,
    question_text TEXT,
    category TEXT,
    difficulty TEXT,
    is_adversarial INTEGER,
    adversarial_category TEXT,
    rufus_answer TEXT,
    score_helpfulness REAL,
    score_accuracy REAL,
    score_hallucination REAL,
    score_safety REAL,
    score_overall REAL,
    anomaly_flagged INTEGER DEFAULT 0,
    anomaly_reason TEXT
);

CREATE TABLE eval_runs (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    mode TEXT,
    total_questions INTEGER,
    avg_overall REAL,
    avg_helpfulness REAL,
    avg_accuracy REAL,
    avg_hallucination REAL,
    avg_safety REAL
);
```

---

## Step 2 — Build anomaly detector

Class: AnomalyDetector in backend/evaluation/anomaly.py

```python
class AnomalyDetector:
    def __init__(self, db_path: str, window: int = 20):
        self.db_path = db_path
        self.window = window  # rolling window size

    async def check(self, result: dict) -> dict:
        # Get rolling average of last N results for same category
        # Flag if current score is more than 2 std devs below average
        # Return result with anomaly_flagged and anomaly_reason added
        pass

    async def get_rolling_stats(self, category: str) -> dict:
        # Return mean and std dev for each dimension for this category
        pass
```

Anomaly threshold: flag if score is more than 1.5 standard deviations
below the rolling mean for that category.

---

## Step 3 — Update pipeline to save results

Update backend/evaluation/pipeline.py:
- After each eval, run anomaly check
- Save result (with anomaly flag) to SQLite
- Return result including anomaly info

---

## Step 4 — Verify storage

```bash
python backend/scripts/test_pipeline.py  # run 10 evals
python -c "
import sqlite3
conn = sqlite3.connect('backend/data/eval_results.db')
rows = conn.execute('SELECT COUNT(*) FROM eval_results').fetchone()
print(f'Stored results: {rows[0]}')
"
```

---

## Phase 6 complete when:
- SQLite DB created with correct schema
- All eval results saved after each run
- Anomaly detection flags outliers correctly
- Rolling stats computed per category

---
---

# Phase 7 — FastAPI Backend (All Endpoints)

## Goal
Build the full REST API that the Next.js frontend will call.
All endpoints read from SQLite. No LLM calls happen via the API
(evals are run via scripts, not triggered by the frontend).

---

## Step 1 — Build main.py

File: backend/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Rufus Eval Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-url.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Step 2 — Build all endpoints

### GET /health
Returns API status and DB stats.
```json
{"status": "ok", "total_evals": 200, "last_run": "2025-03-15T14:22:00Z"}
```

### GET /evals
Returns paginated list of eval results.
Query params: page, limit, category, difficulty, is_adversarial, min_score, max_score
```json
{
  "total": 200,
  "page": 1,
  "results": [...]
}
```

### GET /evals/{eval_id}
Returns single eval result with full detail.

### GET /stats/overview
Returns dashboard KPIs:
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
Returns avg scores broken down by question category.
```json
[
  {"category": "headphones", "avg_overall": 7.9, "count": 45},
  {"category": "laptops", "avg_overall": 7.2, "count": 38},
  ...
]
```

### GET /stats/trend
Returns score trend over time (for the line chart).
Query param: days (default 7)
```json
[
  {"date": "2025-03-10", "avg_overall": 7.1},
  {"date": "2025-03-11", "avg_overall": 7.4},
  ...
]
```

### GET /stats/anomalies
Returns all flagged anomalies.
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
Returns adversarial results summary by failure mode.

---

## Step 3 — Run and test locally

```bash
uvicorn backend.main:app --reload --port 8000
```

Test each endpoint in browser or with curl:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/stats/overview
curl http://localhost:8000/evals?page=1&limit=10
```

---

## Phase 7 complete when:
- All 8 endpoints implemented and returning correct data
- CORS configured for localhost:3000
- API docs auto-generated at http://localhost:8000/docs
- All endpoints handle empty DB gracefully (return empty arrays not errors)

---
---

# Phase 8 — Next.js Frontend (All 4 Screens)

## Goal
Build the dashboard. Four screens, clean black/white aesthetic with red accents,
data fetched from the FastAPI backend. Recharts for all visualisations.

---

## Design system
- Background: white (#FFFFFF)
- Primary text: near-black (#111111)
- Accent: red (#DC2626)
- Secondary: gray (#6B7280)
- Border: light gray (#E5E7EB)
- Font: Inter (system)
- All charts use the same color palette: #DC2626 primary, #111111 secondary, #6B7280 tertiary

---

## Step 1 — Build lib/api.ts

All fetch calls in one place. No inline fetching in components.

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getOverview() { ... }
export async function getEvals(params: EvalParams) { ... }
export async function getEvalById(id: string) { ... }
export async function getStatsByCategory() { ... }
export async function getScoreTrend(days: number) { ... }
export async function getAnomalies() { ... }
export async function getAdversarialSummary() { ... }
```

---

## Step 2 — Build shared components

### ScoreCard.tsx
```
┌─────────────────┐
│  Avg Score      │
│  7.4 / 10      │
│  ▲ +0.3 today  │
└─────────────────┘
```
Props: title, value, subtitle, trend

### AnomalyBadge.tsx
Red pill badge: "12 anomalies"
Props: count

### ScoreTrendChart.tsx
Line chart using Recharts.
X axis: date, Y axis: score 0-10
Red line for overall score.
Props: data (array of {date, avg_overall})

### CategoryBarChart.tsx
Horizontal bar chart.
Each bar = one category, length = avg score.
Props: data (array of {category, avg_overall, count})

### AnswerTable.tsx
Table with columns: question, category, overall score, scores breakdown, anomaly flag.
Expandable row shows full Rufus answer and judge reasoning.
Props: evals, onPageChange

---

## Step 3 — Build Overview screen (app/page.tsx)

Layout:
```
Row 1: 4 KPI cards (avg overall, avg helpfulness, avg accuracy, anomaly count)
Row 2: Score trend line chart (full width)
Row 3: Category bar chart (left) + Recent anomalies list (right)
```

Data: calls getOverview() and getScoreTrend() and getStatsByCategory()

---

## Step 4 — Build Answer Feed (app/feed/page.tsx)

Layout:
```
Filter bar: category dropdown, difficulty dropdown, score range slider, adversarial toggle
Table: all eval results paginated (20 per page)
```

Click a row → expand to show full answer + judge reasoning

---

## Step 5 — Build Weak Spot Analysis (app/analysis/page.tsx)

Layout:
```
Row 1: Category breakdown bar chart (avg score per category)
Row 2: Dimension comparison table (avg of each dimension per category)
Row 3: Worst 10 individual answers (lowest overall score)
```

---

## Step 6 — Build Adversarial Report (app/adversarial/page.tsx)

Layout:
```
Row 1: Summary cards (total adversarial, failure rate, worst failure mode)
Row 2: Failure mode breakdown bar chart
Row 3: Adversarial results table (filterable by failure mode)
Row 4: Export button → downloads results as JSON
```

---

## Phase 8 complete when:
- All 4 screens render without errors
- All data fetched from real FastAPI endpoints
- Charts display correctly with real data
- Table pagination works
- Mobile responsive (Tailwind breakpoints)

---
---

# Phase 9 — Integration + Deployment

## Goal
Wire everything together, do a real API run, deploy backend to Railway
and frontend to Vercel.

---

## Step 1 — Run real evaluation (first live API call)

```bash
# Generate real answers + scores for 20 questions
USE_MOCK=false python backend/scripts/run_eval.py --count 20 --mode standard
```

Watch costs. 20 questions should cost under $0.50.
Verify results saved to SQLite.

---

## Step 2 — Run adversarial suite live

```bash
USE_MOCK=false python backend/scripts/run_adversarial.py --count 10
```

10 adversarial queries. Check failure modes detected correctly.

---

## Step 3 — Run full standard eval

```bash
USE_MOCK=false python backend/scripts/run_eval.py --count 100 --mode standard
```

100 questions. ~$1.50. Verify all stored correctly.

---

## Step 4 — Deploy backend to Railway

1. Create Railway account at railway.app
2. New project → Deploy from GitHub
3. Select rufus-eval-engine repo
4. Set root directory to /backend
5. Add environment variable: ANTHROPIC_API_KEY
6. Railway auto-detects FastAPI and deploys
7. Copy the Railway URL

---

## Step 5 — Deploy frontend to Vercel

1. Push all frontend code to GitHub
2. Connect repo to Vercel
3. Set root directory to /frontend
4. Add environment variable: NEXT_PUBLIC_API_URL = your Railway URL
5. Deploy

---

## Step 6 — Final checks

- [ ] All 4 dashboard screens load in production
- [ ] API endpoints respond correctly from Railway
- [ ] Real eval data visible in dashboard
- [ ] Anomalies detected and flagged
- [ ] Adversarial report populated
- [ ] README updated with live URLs
- [ ] Portfolio site updated with project link

---

## Phase 9 complete when:
- Live URLs working for both frontend and backend
- Real eval data in the dashboard
- README has live demo link
- Portfolio site updated
