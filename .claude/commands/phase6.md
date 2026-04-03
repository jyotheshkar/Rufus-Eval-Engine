# Phase 6 — Anomaly Detection + SQLite Storage

## Goal
Persist all eval results to SQLite and build the anomaly detector that flags
when scores drop significantly vs the rolling average baseline.

---

## Step 1 — Build SQLite schema

File: `backend/evaluation/anomaly.py` (also sets up DB)

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

Class: `AnomalyDetector` in `backend/evaluation/anomaly.py`

```python
class AnomalyDetector:
    def __init__(self, db_path: str, window: int = 20):
        self.db_path = db_path
        self.window = window  # rolling window size

    async def check(self, result: dict) -> dict:
        # Get rolling average of last N results for same category
        # Flag if current score is more than 1.5 std devs below average
        # Return result with anomaly_flagged and anomaly_reason added
        pass

    async def get_rolling_stats(self, category: str) -> dict:
        # Return mean and std dev for each dimension for this category
        pass
```

Anomaly threshold: flag if score is more than **1.5 standard deviations** below
the rolling mean for that category.

---

## Step 3 — Update pipeline to save results

Update `backend/evaluation/pipeline.py`:
- After each eval, run anomaly check
- Save result (with anomaly flag) to SQLite via aiosqlite
- Return result including anomaly info

---

## Step 4 — Enable SQLite MCP

In `.claude/settings.json`, change `"disabled": true` to `"disabled": false` under `mcpServers.sqlite`.
Restart Claude Code so MCP can connect to the live DB.

---

## Step 5 — Verify storage

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
- SQLite MCP enabled in `settings.json`
- Tests pass
- `docs/phase-6.md` generated
