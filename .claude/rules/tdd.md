# TDD Protocol — Rufus Eval Engine

## What TDD means in this project

Test Driven Development here means: every phase ends with a dedicated testing gate
before it is declared complete. Tests are not an afterthought — they are the proof
that the phase is genuinely done, not just "looks done."

The TDD gate runs after all phase code is written. Tests are presented as a plan,
approved by the user, then executed. If any test fails, the root cause is fixed
before the phase can be declared complete.

---

## TDD gate structure

After all phase code is written, present a TDD Plan in this format:

```
## Phase X — TDD Plan

### Tests that will be written
| Test file | Function tested | Scenario | What passing proves |
|-----------|----------------|----------|---------------------|
| backend/tests/test_X.py | function_name | happy path | basic functionality works |
| backend/tests/test_X.py | function_name | edge case | handles empty input |

### Scalability checks
[How this phase's code handles growth]

### Maintainability checks
[What makes this code easy to modify]
```

Wait for user approval, then write and run all tests.

---

## Test requirements per phase

### Phase 1 — Data Generation
- Verify `products.json` schema (all required fields present for every product)
- Verify category distribution (10 categories, correct counts)
- Verify `questions.json` schema (all required fields, correct difficulty distribution)
- Verify `adversarial.json` schema (all required fields, correct category distribution)
- No API calls in tests — tests read from JSON files only

### Phase 2 — FAISS Retrieval
- Retriever returns exactly 5 results for a valid query
- Results are sorted by relevance (most similar first)
- Retriever handles a query that matches no products gracefully
- Embeddings are non-zero (sanity check that sentence-transformers ran)
- No API calls — embeddings are pre-computed

### Phase 3 — Rufus Agent
- Agent returns a non-empty answer string
- Answer references at least one of the retrieved products
- Agent handles empty product list without crashing
- Mock returns correct shape when `USE_MOCK=true`

### Phase 4 — LLM Judge
- Judge returns all 4 scores: helpfulness, accuracy, hallucination, safety
- All scores are floats between 0 and 10
- Judge handles an empty Rufus answer without crashing
- Pipeline test: question → retrieval → Rufus → judge → scores (full end-to-end with mocks)

### Phase 5 — Adversarial Suite
- All 50 adversarial queries produce a result
- Each result is tagged with the correct failure mode category
- Summary report contains all 5 failure mode categories
- Failure rates are non-zero (adversarial queries should be harder)

### Phase 6 — Anomaly Detection + SQLite
- Eval result is saved to SQLite after a pipeline run
- Anomaly detector flags a score artificially set 2 std devs below mean
- Anomaly detector does not flag a normal score
- Rolling stats return correct mean and std dev for a known dataset

### Phase 7 — FastAPI Backend
- Every endpoint returns HTTP 200 with correct response shape
- Every endpoint returns correct error shape when given bad input
- Pagination works: page 1 and page 2 return different results
- Empty DB returns empty arrays, not errors

### Phase 8 — Next.js Frontend
- Each component renders without crashing
- ScoreCard displays the score and label it is given
- AnomalyBadge shows the correct count
- All API calls are mocked in tests — no real network calls

### Phase 9 — Integration
- End-to-end: real API call (20 questions, `USE_MOCK=false`) completes without error
- All results stored in SQLite (count verified)
- Frontend fetches from live backend URL (manual verification)

---

## What "scalable and maintainable" means for this project

### Scalable
Code is scalable if it still works correctly when:
- Product count grows from 1000 to 100,000
- Question count grows from 200 to 10,000
- Eval results grow from 200 to 1,000,000 rows in SQLite
- More dimensions are added to the judge (e.g., a 5th dimension)

Tests for scalability: run with full dataset sizes, not toy samples.

### Maintainable
Code is maintainable if:
- The judge prompt can be changed in one place without touching pipeline logic
- A new question category can be added without changing any scoring code
- A new API endpoint can be added by following the same pattern as existing ones
- A frontend chart can be swapped without changing data fetching logic

---

## Rules

- Never skip tests with `pytest.mark.skip` without a comment explaining why and a TODO
- Never use `assert True` or empty tests to get a passing suite
- Never call the live Anthropic API in tests — always use mocks
- If a test reveals a bug, fix the bug — do not adjust the test to pass around it
- Tests live in `backend/tests/` (Python) and `frontend/__tests__/` (TypeScript)
