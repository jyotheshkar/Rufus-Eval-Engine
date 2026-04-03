# Phase 3 — Rufus Agent (Shopping Assistant)
**Status:** Complete
**Date completed:** 2026-04-03
**Built by:** Claude (claude-sonnet-4-6) + Jyothesh Karnam

---

## What this phase built

The shopping assistant brain of the system. Given a customer's question and a list of relevant products (from the FAISS retriever), the Rufus agent generates a natural, grounded shopping answer — exactly like Amazon's Rufus would. During development it returns a cached mock response; in production it calls Claude Haiku.

---

## Why this phase matters

Retrieval alone doesn't help a customer — they need a coherent recommendation in plain English. Rufus is the layer that turns a list of product dictionaries into a helpful answer. Phase 4 (the judge) will evaluate the quality of these answers, so getting the answer format right here directly determines what the judge can measure.

---

## What was built

### RufusAgent class
**File:** `backend/agents/rufus_agent.py`
**What it does:** Accepts a query string and a list of up to 5 retrieved products. Formats the products into a structured context block, combines it with the customer query, and sends both to Claude Haiku with a carefully written system prompt. Returns a dict containing the answer, model name, query, list of product IDs used, and token usage.
**Key decisions made:**
- `use_mock` defaults to reading `USE_MOCK` from the environment — no hardcoding, no accidental live calls
- The Anthropic client is only instantiated when `use_mock=False` — calling the class in mock mode has zero API overhead
- System prompt is a module-level constant so it can be edited in one place without touching any other logic
- `max_tokens=400` keeps answers concise and costs predictable

### mock_rufus.json — mock response
**File:** `backend/data/mocks/mock_rufus.json`
**What it does:** A static JSON file containing a realistic Rufus-style answer. Any call to `generate_answer()` with `USE_MOCK=true` returns this instead of hitting the API. Token usage is reported as zero to reflect no real cost.

### test_rufus_agent.py — smoke test script
**File:** `backend/scripts/test_rufus_agent.py`
**What it does:** Wires the FAISS retriever and Rufus agent together end-to-end for 3 test queries. Loads the pre-built FAISS index, retrieves 5 products per query, passes them to Rufus, and prints the answer with word count and product count. Respects `USE_MOCK` from the environment.

---

## How data flows through this phase

1. A query string arrives (e.g. "best wireless headphones under £100")
2. `FAISSRetriever.search(query, k=5)` returns 5 relevant product dicts
3. `RufusAgent._build_product_context(products)` formats them into a numbered list with price, rating, specs, and description
4. `RufusAgent._build_user_prompt(query, context)` combines query + context into the user message
5. If `USE_MOCK=true`: load `mock_rufus.json` and return the static answer immediately
6. If `USE_MOCK=false`: send system prompt + user message to Claude Haiku, return the generated answer
7. Result dict is returned with: answer, model, query, products_used (list of IDs), usage (token counts)

---

## Tests written

| Test | What it checks | Why it matters |
|------|---------------|----------------|
| `test_generate_answer_returns_non_empty_string` | Answer is a non-empty string | Basic contract — agent must always return something |
| `test_generate_answer_result_has_all_required_keys` | Result has all 5 required keys | Downstream phases (judge, pipeline) depend on this shape |
| `test_generate_answer_model_is_mock_when_use_mock_true` | model field = "mock" | Confirms mock guard is active — no surprise API calls |
| `test_generate_answer_products_used_matches_input` | products_used = input product IDs | Traceability — we know which products influenced the answer |
| `test_generate_answer_empty_products_does_not_crash` | Empty product list handled gracefully | FAISS may return 0 results for very unusual queries |
| `test_generate_answer_query_echoed_in_result` | query field matches input | Result is self-contained — no need to re-pass query downstream |
| `test_build_product_context_includes_product_name_and_price` | Product name and price appear in context | Ensures Rufus has the right facts to cite |
| `test_build_product_context_empty_returns_fallback` | Empty products returns fallback string | Rufus can still respond honestly when retrieval finds nothing |

---

## Checkpoint verification

- ✓ `backend/agents/rufus_agent.py` fully implemented
- ✓ Agent correctly uses retrieved products in its answer
- ✓ Mock response in `backend/data/mocks/mock_rufus.json`
- ✓ Mock guard active: returns mock when `USE_MOCK=true`
- ✓ Agent handles empty retrieval results gracefully
- ✓ `docs/phase-3.md` generated

---

## Known limitations

In mock mode, every query returns the same response regardless of the question or products. This is intentional for budget protection — the answer content is not evaluated until Phase 9's live run. The mock is realistic enough for the judge to score in Phase 4.

---

## What comes next

Phase 4 builds the LLM judge pipeline. It takes Rufus's answer and scores it on 4 dimensions (helpfulness, accuracy, hallucination, safety) using a second Claude Haiku call, also protected by the mock guard.
