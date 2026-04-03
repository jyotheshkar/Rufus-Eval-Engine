# Phase 4 — LLM Judge Pipeline (4-Dimension Scoring)
**Status:** Complete
**Date completed:** 2026-04-03
**Built by:** Claude (claude-sonnet-4-6) + Jyothesh Karnam

---

## What this phase built

The evaluation intelligence of the system. A second Claude Haiku instance reads every Rufus answer alongside the original question and the products that were available, then scores the answer on four dimensions: helpfulness, accuracy, hallucination, and safety. An orchestration pipeline wires all three components (retriever, Rufus, judge) into a single call that runs a complete evaluation end-to-end.

---

## Why this phase matters

Without the judge, there is no way to automatically measure answer quality. Every score that appears in the dashboard, every anomaly flag, every adversarial failure report — all of it flows from what was built here. This is the core intelligence of the whole system.

---

## What was built

### JudgeAgent class
**File:** `backend/agents/judge_agent.py`
**What it does:** Takes a query, a list of retrieved products, and a Rufus answer. Sends them to Claude Haiku with a detailed scoring rubric and asks for a structured JSON response with scores and reasoning for each of the four dimensions. Parses the response, computes a weighted overall score, and returns a clean result dict.
**Key decisions made:**
- Weighted overall: helpfulness 30% + accuracy 30% + hallucination 30% + safety 10% — safety is weighted lower because most normal answers pass it; the other three dimensions differentiate answer quality
- JSON parsing strips markdown code fences before parsing — Claude sometimes wraps JSON in ` ```json ``` ` blocks
- Same `use_mock` pattern as RufusAgent — reads `USE_MOCK` from environment, no accidental live calls

### mock_judge.json — mock judge response
**File:** `backend/data/mocks/mock_judge.json`
**What it does:** Static JSON file with realistic scores and reasoning for all four dimensions. Used whenever `USE_MOCK=true`. Scores: helpfulness 8, accuracy 9, hallucination 9, safety 10, overall 9.0.

### EvalPipeline class
**File:** `backend/evaluation/pipeline.py`
**What it does:** Orchestrates the full evaluation loop. `run_single(question)` does: (1) retrieve 5 products via FAISS, (2) generate a Rufus answer, (3) judge the answer, (4) return a complete result dict with eval ID, timestamp, products, answer, scores, reasoning, and metadata. `run_batch(questions)` runs multiple questions sequentially with a configurable delay.
**Key decisions made:**
- Products are stored as slim dicts in the result (id, name, category only) to keep results compact — full product data is always retrievable from products.json
- `run_batch` uses `asyncio.sleep` between calls to avoid rate limits in live mode; delay defaults to 0.1s (irrelevant in mock mode)
- `is_adversarial` flag passes through to the result so Phase 5 can tag adversarial runs

### test_pipeline.py — smoke test script
**File:** `backend/scripts/test_pipeline.py`
**What it does:** Runs 3 real questions through the full pipeline and prints scores, reasoning summary, and answer preview for each. Used to visually verify the end-to-end flow.

---

## How data flows through this phase

1. A question dict arrives at `EvalPipeline.run_single(question)`
2. `FAISSRetriever.search(query, k=5)` returns 5 relevant products
3. `RufusAgent.generate_answer(query, products)` returns a shopping answer
4. `JudgeAgent.score(query, products, answer)` returns scores + reasoning for all 4 dimensions
5. `_compute_overall()` calculates the weighted average across dimensions
6. A complete eval result dict is assembled with a unique UUID, UTC timestamp, and all components
7. The result is returned to the caller (Phase 6 will save it to SQLite)

---

## Tests written

| Test | What it checks | Why it matters |
|------|---------------|----------------|
| `test_judge_returns_all_four_dimensions` | All 4 dimension keys present | Downstream code depends on all 4 keys existing |
| `test_judge_scores_are_floats_in_range` | Every score is 0.0–10.0 | Scores outside range would corrupt dashboard metrics |
| `test_judge_returns_overall_score` | Overall score present and in range | Required for anomaly detection in Phase 6 |
| `test_judge_model_is_mock` | model = "mock" in mock mode | Confirms mock guard — no surprise API costs |
| `test_judge_handles_empty_answer` | No crash on empty answer string | Edge case: Rufus could theoretically return empty |
| `test_judge_handles_empty_products` | No crash on empty product list | Edge case: FAISS may return 0 results |
| `test_judge_compute_overall_weighted_average` | 10/10/10/0 → 9.0 | Verifies exact weighting formula |
| `test_judge_parse_valid_json` | Clean JSON parsed correctly | Core parsing contract |
| `test_judge_parse_json_with_code_fence` | Markdown-wrapped JSON handled | Claude sometimes wraps JSON in code fences |
| `test_pipeline_run_single_returns_all_required_keys` | All required keys in result | Downstream phases depend on this shape |
| `test_pipeline_run_single_scores_have_all_dimensions` | All 5 score keys present | API endpoint in Phase 7 returns these fields |
| `test_pipeline_run_single_retrieves_five_products` | Exactly 5 products retrieved | Rufus and judge always have full context |
| `test_pipeline_run_single_is_adversarial_false_by_default` | Flag defaults to False | Phase 5 adversarial runs must explicitly set True |
| `test_pipeline_run_batch_returns_correct_count` | N questions → N results | Batch processing integrity |
| `test_pipeline_run_batch_adversarial_flags_results` | adversarial mode sets flag | Phase 5 depends on this for failure mode tracking |

---

## Checkpoint verification

- ✓ `backend/agents/judge_agent.py` fully implemented
- ✓ All 4 dimensions scored: helpfulness, accuracy, hallucination, safety
- ✓ Scores are floats in range 0–10
- ✓ Mock response in `backend/data/mocks/mock_judge.json`
- ✓ Mock guard active
- ✓ `backend/evaluation/pipeline.py` wires retrieval → Rufus → judge
- ✓ End-to-end pipeline runs for 3 questions with mocks
- ✓ `docs/phase-4.md` generated

---

## Known limitations

In mock mode, every question gets identical scores (8/9/9/10) regardless of query or answer content. This is by design — real scoring requires a live API call. The mock values are realistic enough for testing Phase 5–8 without triggering the budget.

---

## What comes next

Phase 5 feeds all 50 adversarial queries through the pipeline and builds a failure mode report that shows which categories (missing info traps, price traps, etc.) cause the most quality degradation.
