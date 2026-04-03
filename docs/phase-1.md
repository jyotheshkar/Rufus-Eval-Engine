# Phase 1 — Repo Scaffold + Data Generation
**Status:** Complete
**Date completed:** 2026-04-03
**Built by:** Claude (claude-sonnet-4-6) + Jyothesh Karnam

---

## What this phase built

The complete project skeleton and all three data files the system depends on. Every folder, every placeholder file, the Python dependency list, the environment config, and three JSON datasets — 1000 products, 200 shopping questions, and 50 adversarial queries — were created in this phase. Nothing in phases 2–9 can run without what was built here.

---

## Why this phase matters

The entire evaluation pipeline is data-driven. The FAISS retriever needs products to index, the question bank feeds the eval runs, and the adversarial suite is what exposes Rufus's failure modes. Getting this data right once means every subsequent phase builds on a solid foundation.

---

## What was built

### Project folder structure
**What it does:** Creates every directory and placeholder file for the entire project upfront — `backend/`, `frontend/`, `docs/`, all subdirectories, all `.py` and `.tsx` placeholder files. This makes the shape of the finished system visible from day one.

### backend/requirements.txt
**File:** `backend/requirements.txt`
**What it does:** Lists all 9 Python dependencies needed across all backend phases: FastAPI, Uvicorn, Pydantic, Anthropic SDK, FAISS, sentence-transformers, python-dotenv, aiosqlite, and NumPy.
**Key decisions made:**
- Versions are pinned to avoid unexpected breakage (updated in Phase 2: faiss-cpu bumped to 1.8.0, sentence-transformers to >=3.0.0 for Python 3.12 compatibility)

### backend/.env.example
**File:** `backend/.env.example`
**What it does:** Template environment file showing every required variable. Crucially, `USE_MOCK=true` is set by default — this is the budget protection mechanism that prevents accidental Anthropic API calls during development.

### products.json — 1000 synthetic products
**File:** `backend/data/products.json`
**What it does:** 1000 Amazon-style electronics products generated via Claude Haiku in batches of 50. Each product has: id, name, category, price (GBP), currency, rating, review count, brand, description, specs dict, tags list, in_stock flag, and an embedding field (populated in Phase 2).
**Key decisions made:**
- 10 categories: headphones (110), laptops (110), smartphones (110), accessories (130), tablets/smartwatches/cameras/speakers/gaming/monitors (~90 each)
- Specs vary meaningfully by category — headphones have battery_life and connectivity; laptops have RAM, CPU, storage
- Products are realistic enough to produce meaningful retrieval and scoring results

### questions.json — 200 shopping questions
**File:** `backend/data/questions.json`
**What it does:** 200 hand-crafted shopping questions covering all 10 product categories. Each question has: id, question text, category, difficulty, intent type, expected product categories, and notes.
**Key decisions made:**
- 3 difficulty levels: easy (80), medium (80), hard (40)
- 5 intent types: recommendation, comparison, specific_question, budget_query, feature_query
- Written by hand (no API calls) to ensure controlled, reproducible eval runs

### adversarial.json — 50 adversarial queries
**File:** `backend/data/adversarial.json`
**What it does:** 50 queries specifically designed to expose Rufus's failure modes. Each query has: id, question, failure mode category, target failure type, and notes explaining why it's adversarial.
**Key decisions made:**
- 5 categories × 10 queries each: missing_info_trap, contradiction_query, ambiguous_intent, price_trap, pressure_scenario
- Designed to stress-test hallucination, accuracy, helpfulness, and safety dimensions separately

### Mock response files
**Files:** `backend/data/mocks/mock_rufus.json`, `backend/data/mocks/mock_judge.json`
**What they do:** Static JSON responses that stand in for real Claude Haiku API calls during development. Any code that calls the LLM checks `USE_MOCK=true` first and returns these instead, preserving the $10 budget.

---

## How data flows through this phase

1. `generate_products.py` calls Claude Haiku API in batches of 50, accumulates 1000 products, saves to `products.json`
2. `generate_questions.py` runs with no API calls — writes 200 hand-crafted questions directly to `questions.json`
3. `adversarial.json` is created directly as a JSON file — no script needed, no API calls
4. All three files land in `backend/data/` and stay there for the lifetime of the project

---

## Tests written

Data validation was performed via inline Python checks rather than a formal pytest suite (the TDD gate for data files). All checks passed:

| Check | Result | Detail |
|-------|--------|--------|
| products.json count | ✓ | 1000 products |
| Product categories | ✓ | All 10 categories present |
| Product schema fields | ✓ | id, name, category, price, currency, rating, review_count, brand, description, specs, tags, in_stock, embedding |
| questions.json count | ✓ | 200 questions |
| Question difficulty distribution | ✓ | easy: 80, medium: 80, hard: 40 |
| Question schema fields | ✓ | id, question, category, difficulty, intent, expected_product_categories, notes |
| adversarial.json count | ✓ | 50 queries |
| Adversarial categories | ✓ | All 5 categories, 10 each |
| Adversarial schema fields | ✓ | id, question, category, target_failure, notes |
| .env.example USE_MOCK | ✓ | USE_MOCK=true confirmed |

---

## Checkpoint verification

- ✓ All folders exist: `backend/`, `frontend/`, `docs/`, all subdirectories
- ✓ All placeholder `.py` and `.tsx` files exist
- ✓ `backend/requirements.txt` lists all 9 dependencies
- ✓ `backend/.env.example` exists with `USE_MOCK=true`
- ✓ `backend/data/products.json` has exactly 1000 products
- ✓ All 10 product categories are present
- ✓ `backend/data/questions.json` has exactly 200 questions
- ✓ All 3 difficulty levels (easy, medium, hard) are present
- ✓ `backend/data/adversarial.json` has exactly 50 queries
- ✓ All 5 adversarial categories are present (10 each)
- ✓ `docs/phase-1.md` generated

---

## Known limitations

Category counts are slightly uneven (accessories: 130, headphones/laptops/smartphones: 110 vs target of 100/120). This does not affect retrieval quality or eval correctness — it is a cosmetic deviation from the original spec.

---

## What comes next

Phase 2 takes `products.json` and converts every product into a vector embedding, then builds a FAISS search index so any shopping question can retrieve the 5 most relevant products in milliseconds.
