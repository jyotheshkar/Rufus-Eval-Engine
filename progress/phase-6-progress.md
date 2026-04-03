# Phase 6 Progress — Anomaly Detection + SQLite Storage
**Completed:** 2026-04-03
**Phase status:** Complete

---

## What was done
- Implemented `AnomalyDetector` class with `check()`, `save_result()`, `save_run()`, and `get_rolling_stats()`
- Implemented `init_db()` creating `eval_results` and `eval_runs` tables with full schema
- Updated `EvalPipeline.run_single()` to run anomaly check and save every result to SQLite
- Added `db_path` param to `EvalPipeline` and `AnomalyDetector` for test isolation
- Implemented `run_eval.py` CLI script — ran 10 questions successfully, DB verified
- Fixed anomaly threshold to handle zero std dev case (absolute drop fallback)
- Enabled SQLite MCP server in `.claude/settings.json`
- Wrote 9 pytest tests — 1 failed on first run (fixed), all 9 passing on second run

## Files created or modified
| File | Change |
|------|--------|
| `backend/evaluation/anomaly.py` | Implemented — AnomalyDetector + init_db + SQLite schema |
| `backend/evaluation/pipeline.py` | Modified — anomaly check + save after run_single, db_path param |
| `backend/scripts/run_eval.py` | Implemented — CLI eval runner with DB storage |
| `.claude/settings.json` | Modified — SQLite MCP enabled (disabled: false) |
| `backend/tests/test_phase6.py` | Created — 9 pytest tests |
| `docs/phase-6.md` | Created — phase documentation |
| `progress/phase-6-progress.md` | Created — this file |

## Test results
- Tests written: 9
- Tests passed: 9
- Tests failed: 0 (1 failure on first run — fixed root cause)

## Checkpoint status
All checkpoint criteria met: Yes

## Issues encountered
- `test_anomaly_flagged_for_score_far_below_mean` failed: when all seeded scores are identical (9.0), std dev = 0, so `std > 0` condition never triggered. Fixed by adding absolute drop fallback: flag if std=0 and drop > 2.0 points.

## Notes for next phase
- DB path: `backend/data/eval_results.db` — gitignored, must be created by running `run_eval.py` or `init_db()`
- Phase 7 API reads from `eval_results` and `eval_runs` tables
- `anomaly_flagged` is an INTEGER (0/1) in SQLite — convert to bool when returning from API
- SQLite MCP is now active — Claude can query the DB directly in future sessions
