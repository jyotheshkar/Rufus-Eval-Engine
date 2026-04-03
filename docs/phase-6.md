# Phase 6 — Anomaly Detection + SQLite Storage
**Status:** Complete
**Date completed:** 2026-04-03
**Built by:** Claude (claude-sonnet-4-6) + Jyothesh Karnam

---

## What this phase built

Persistent storage and automatic quality monitoring. Every eval result is now saved to a SQLite database after each run. An anomaly detector watches each result's score and flags it if it drops significantly below the rolling average for its category — making quality regressions visible without manual inspection.

---

## Why this phase matters

Without storage, every eval run is ephemeral — you can't track trends, compare runs, or spot regressions. Without anomaly detection, score drops go unnoticed until someone manually reviews the data. This phase makes the eval system self-monitoring: it saves everything and raises a flag when something looks wrong.

---

## What was built

### AnomalyDetector class + init_db()
**File:** `backend/evaluation/anomaly.py`
**What it does:** Two responsibilities in one file. `init_db()` creates the SQLite database with the correct schema if it doesn't exist. `AnomalyDetector` provides three async methods: `check()` compares a result's overall score against the rolling category mean and flags it if the drop exceeds the threshold; `save_result()` persists a full eval result to `eval_results`; `save_run()` saves a run-level summary to `eval_runs`.

**Anomaly threshold:** Flag if score drops more than 1.5 standard deviations below the rolling category mean. When std dev is zero (all scores identical), flag if the absolute drop exceeds 2.0 points.

**Key decisions made:**
- Rolling window of 20 results per category — enough history to be meaningful, small enough to detect recent regressions
- `INSERT OR REPLACE` — re-running the same eval ID updates rather than errors
- Threshold handles zero std dev edge case (uniform scores) with absolute drop fallback

### SQLite schema
**Tables:** `eval_results`, `eval_runs`

`eval_results` stores one row per eval: id, timestamp, question metadata, Rufus answer, all 4 dimension scores, overall score, anomaly flag, anomaly reason, and adversarial fields.

`eval_runs` stores one row per batch run: id, timestamp, mode, question count, and average scores across all dimensions.

### Updated EvalPipeline
**File:** `backend/evaluation/pipeline.py`
**What changed:** `run_single()` now runs `anomaly.check()` and `anomaly.save_result()` after every eval. The pipeline accepts an optional `db_path` parameter so tests can use a temporary database without touching the real one.

### Updated run_eval.py
**File:** `backend/scripts/run_eval.py`
**What it does:** CLI script (`--mock`, `--limit N`) that initialises the DB, runs N standard questions through the pipeline, saves a run summary, and prints aggregate stats including anomaly count.

---

## How data flows through this phase

1. `run_eval.py` calls `init_db()` to ensure tables exist
2. For each question, `EvalPipeline.run_single()` runs the full retrieval → answer → judge flow
3. The result dict is passed to `AnomalyDetector.check()` which queries the last 20 results for that category from SQLite, computes mean and std dev, and sets `anomaly_flagged` + `anomaly_reason`
4. `AnomalyDetector.save_result()` writes the result (including anomaly fields) to `eval_results`
5. After all questions, `save_run()` writes the aggregate summary to `eval_runs`
6. Phase 7's API reads from both tables to power the dashboard

---

## Tests written

| Test | What it checks | Why it matters |
|------|---------------|----------------|
| `test_init_db_creates_tables` | Both tables created by init_db | Schema must exist before any reads/writes |
| `test_save_result_persists_to_db` | Result row written to DB | Core storage contract |
| `test_anomaly_not_flagged_with_insufficient_history` | No flag when < 2 history rows | Can't detect anomalies without baseline |
| `test_anomaly_not_flagged_for_normal_score` | Normal score not flagged | No false positives on healthy results |
| `test_anomaly_flagged_for_score_far_below_mean` | Score 2+ std devs below mean gets flagged | Core anomaly detection contract |
| `test_rolling_stats_returns_correct_mean` | Mean of [8, 9, 10] = 9.0 | Stats computation is correct |
| `test_rolling_stats_empty_category_returns_zero` | Unknown category returns count=0 | Graceful handling of new categories |
| `test_pipeline_result_includes_anomaly_fields` | anomaly_flagged and anomaly_reason in result | Downstream API needs these fields |
| `test_pipeline_saves_result_to_db` | DB has 1 row after run_single | Full pipeline integration check |

---

## Checkpoint verification

- ✓ `eval_results` and `eval_runs` tables created with correct schema
- ✓ All eval results saved to SQLite after each run
- ✓ Anomaly detector flags results > 1.5 std devs below category mean
- ✓ Rolling stats computed correctly per category
- ✓ SQLite MCP server enabled in `settings.json`
- ✓ `docs/phase-6.md` generated

---

## Known limitations

The anomaly detector only monitors the `overall` score, not individual dimensions. A result where hallucination drops badly but other scores stay high might not be flagged. Phase 7 exposes per-dimension scores in the API so the frontend can visualise this.

---

## What comes next

Phase 7 builds the FastAPI backend — 8 endpoints that expose eval results, run summaries, adversarial reports, and anomaly data as a REST API for the Next.js dashboard.
