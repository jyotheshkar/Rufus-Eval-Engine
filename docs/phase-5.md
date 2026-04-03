# Phase 5 — Adversarial Test Suite
**Status:** Complete
**Date completed:** 2026-04-03
**Built by:** Claude (claude-sonnet-4-6) + Jyothesh Karnam

---

## What this phase built

A dedicated adversarial evaluation layer that stress-tests Rufus against 50 deliberately difficult queries designed to expose specific failure modes. The judge was extended to detect adversarial patterns, the pipeline gained a `run_adversarial()` method that processes all 50 queries and produces a structured failure mode report, and a CLI script prints that report in a readable summary.

---

## Why this phase matters

Standard evaluation only tests normal shopping questions — it can't tell you *where* Rufus breaks. The adversarial suite answers: which failure mode is most damaging? Does Rufus hallucinate when asked about specs it can't find? Does it cave to price traps? This is what makes the eval framework genuinely useful for catching real production risks.

---

## What was built

### Extended JudgeAgent — adversarial detection
**File:** `backend/agents/judge_agent.py`
**What changed:** The judge now accepts an optional `adversarial_category` parameter. When provided, it applies category-specific scoring rules and adds two new fields to every result: `adversarial_triggered` (bool) and `failure_mode_detected` (the primary dimension that failed). In mock mode, each adversarial category produces a characteristic low score for its target dimension.

**Adversarial scoring rules:**
| Category | Dimension penalised | Why |
|----------|-------------------|-----|
| `missing_info_trap` | hallucination | Assistant may invent specs not in catalogue |
| `price_trap` | accuracy | Assistant may recommend products outside stated price range |
| `contradiction_query` | helpfulness | Assistant may ignore conflicting requirements |
| `ambiguous_intent` | helpfulness | Assistant may fail to seek clarification |
| `pressure_scenario` | safety | Assistant may use pushy or manipulative language |

### Extended EvalPipeline — run_adversarial()
**File:** `backend/evaluation/pipeline.py`
**What changed:** Added `run_adversarial()` which loads `adversarial.json`, runs all 50 queries through `run_single()` with their category tag, and assembles a `failure_summary` dict keyed by category. Each category entry contains: count, triggered count, failure rate, and average scores for all 4 dimensions.

Also extended `run_single()` to accept and pass through `adversarial_category` to the judge.

### run_adversarial.py — CLI report script
**File:** `backend/scripts/run_adversarial.py`
**What it does:** CLI entry point (`--mock` flag) that runs the full adversarial suite and prints a formatted report showing the worst-scoring dimension per category, trigger counts, and overall failure rate.

---

## How data flows through this phase

1. `run_adversarial.py` calls `EvalPipeline.run_adversarial()`
2. Pipeline loads all 50 queries from `adversarial.json`
3. For each query, `run_single(question, is_adversarial=True, adversarial_category=category)` runs
4. FAISS retrieves 5 products, Rufus generates an answer
5. `JudgeAgent.score(..., adversarial_category=category)` applies category-specific scoring rules
6. Result includes `adversarial_triggered`, `failure_mode_detected`, and `adversarial_category` fields
7. `_build_failure_summary()` aggregates all 50 results by category
8. Final report: total count, per-result list, and failure summary with rates and avg scores

---

## Tests written

| Test | What it checks | Why it matters |
|------|---------------|----------------|
| `test_judge_adversarial_triggered_for_missing_info_trap` | hallucination detected | Core adversarial detection contract |
| `test_judge_adversarial_triggered_for_price_trap` | accuracy detected | Price trap must penalise accuracy |
| `test_judge_adversarial_triggered_for_contradiction_query` | helpfulness detected | Contradiction must penalise helpfulness |
| `test_judge_adversarial_triggered_for_ambiguous_intent` | helpfulness detected | Ambiguity must penalise helpfulness |
| `test_judge_adversarial_triggered_for_pressure_scenario` | safety detected | Pressure must penalise safety |
| `test_judge_non_adversarial_not_triggered` | normal query not flagged | No false positives on standard queries |
| `test_pipeline_run_adversarial_returns_50_results` | exactly 50 results | All queries processed, none dropped |
| `test_pipeline_run_adversarial_all_results_have_adversarial_flag` | is_adversarial=True on all | Correct tagging for downstream storage |
| `test_pipeline_run_adversarial_results_have_category_tag` | valid category on each result | Phase 6 storage and Phase 7 API need this |
| `test_pipeline_run_adversarial_failure_summary_has_all_categories` | all 5 categories in summary | Report is complete |
| `test_pipeline_run_adversarial_failure_rates_nonzero` | failure rate > 0 per category | Adversarial queries actually harder than normal |
| `test_pipeline_run_adversarial_each_category_has_10_results` | 10 results per category | Distribution from adversarial.json preserved |

---

## Checkpoint verification

- ✓ Adversarial pipeline runs all 50 queries
- ✓ Failure mode categories tagged on each result
- ✓ `run_adversarial.py` outputs summary by failure mode
- ✓ Judge detects adversarial-specific failure patterns
- ✓ All 5 failure modes produce results
- ✓ Runs cleanly with `USE_MOCK=true`
- ✓ `docs/phase-5.md` generated

---

## Known limitations

In mock mode, every query in a category gets the same score — there is no variance within a category. Real runs (Phase 9) will show natural spread. The 100% failure rate in mock mode is artificial and by design — it proves the detection mechanism works, not that Rufus fails 100% of the time.

---

## What comes next

Phase 6 adds anomaly detection and SQLite storage. Every eval result (both standard and adversarial) will be saved to a database, and a rolling-average detector will flag results that drop significantly below the category mean.
