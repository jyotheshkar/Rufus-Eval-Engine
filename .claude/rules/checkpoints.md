# Checkpoints — Rufus Eval Engine

## What are checkpoints

A checkpoint is a set of verifiable criteria that must all be true before a phase is
declared complete. Checkpoints are not optional. A phase with failing tests, missing
files, or unverified data is not complete — even if the code looks correct.

---

## Phase 1 Checkpoint — Repo Scaffold + Data Generation

- [ ] All folders exist: `backend/`, `frontend/`, `docs/`, all subdirectories
- [ ] All placeholder `.py` and `.tsx` files exist
- [ ] `backend/requirements.txt` lists all 9 dependencies
- [ ] `backend/.env.example` exists with `USE_MOCK=true`
- [ ] `backend/data/products.json` has exactly 1000 products
- [ ] All 10 product categories are present with correct counts
- [ ] `backend/data/questions.json` has exactly 200 questions
- [ ] All 3 difficulty levels (easy, medium, hard) are present
- [ ] `backend/data/adversarial.json` has exactly 50 queries
- [ ] All 5 adversarial categories are present (10 each)
- [ ] No Anthropic API calls made except during product generation
- [ ] `docs/phase-1.md` generated

---

## Phase 2 Checkpoint — FAISS Vector Store

- [ ] `backend/retrieval/faiss_retriever.py` fully implemented
- [ ] FAISS index built from all 1000 products
- [ ] `products.json` updated with embeddings for all products
- [ ] Top-5 retrieval returns semantically relevant results
- [ ] Retrieval tested with at least 3 sample queries
- [ ] Index build script runs cleanly with `USE_MOCK=true`
- [ ] `docs/phase-2.md` generated

---

## Phase 3 Checkpoint — Rufus Agent

- [ ] `backend/agents/rufus_agent.py` fully implemented
- [ ] Agent correctly uses retrieved products in its answer
- [ ] Mock response in `backend/data/mocks/mock_rufus.json`
- [ ] Mock guard active: returns mock when `USE_MOCK=true`
- [ ] Agent handles empty retrieval results gracefully
- [ ] `docs/phase-3.md` generated

---

## Phase 4 Checkpoint — LLM Judge Pipeline

- [ ] `backend/agents/judge_agent.py` fully implemented
- [ ] All 4 dimensions scored: helpfulness, accuracy, hallucination, safety
- [ ] Scores are floats in range 0–10
- [ ] Mock response in `backend/data/mocks/mock_judge.json`
- [ ] Mock guard active
- [ ] `backend/evaluation/pipeline.py` wires retrieval → Rufus → judge
- [ ] End-to-end pipeline runs for one question with mocks
- [ ] `docs/phase-4.md` generated

---

## Phase 5 Checkpoint — Adversarial Suite

- [ ] Adversarial pipeline runs all 50 queries
- [ ] Failure mode categories tagged on each result
- [ ] `run_adversarial.py` outputs summary by failure mode
- [ ] Judge detects adversarial-specific failure patterns
- [ ] All 5 failure modes produce results
- [ ] Runs cleanly with `USE_MOCK=true`
- [ ] `docs/phase-5.md` generated

---

## Phase 6 Checkpoint — Anomaly Detection + SQLite

- [ ] `eval_results` and `eval_runs` tables created with correct schema
- [ ] All eval results saved to SQLite after each run
- [ ] Anomaly detector flags results > 1.5 std devs below category mean
- [ ] Rolling stats computed correctly per category
- [ ] SQLite MCP server enabled in `settings.json`
- [ ] `docs/phase-6.md` generated

---

## Phase 7 Checkpoint — FastAPI Backend

- [ ] All 8 endpoints implemented and returning correct shapes
- [ ] CORS configured for `localhost:3000`
- [ ] API docs auto-generated at `/docs`
- [ ] All endpoints handle empty DB gracefully
- [ ] Every route has a happy-path test and an error test
- [ ] `docs/phase-7.md` generated

---

## Phase 8 Checkpoint — Next.js Frontend

- [ ] All 4 screens render without errors
- [ ] All data fetched through `lib/api.ts` (no inline fetch)
- [ ] Charts display correctly with real data
- [ ] Table pagination works
- [ ] Mobile responsive (Tailwind breakpoints applied)
- [ ] No TypeScript errors (`npm run build` passes)
- [ ] `docs/phase-8.md` generated

---

## Phase 9 Checkpoint — Integration + Deployment

- [ ] Real eval run completed (20+ questions, `USE_MOCK=false`)
- [ ] Real data visible in deployed frontend
- [ ] Backend live on Railway with correct environment variables
- [ ] Frontend live on Vercel with correct `NEXT_PUBLIC_API_URL`
- [ ] All 4 dashboard screens load in production
- [ ] README updated with live URLs
- [ ] `docs/phase-9.md` generated

---

## How to verify a checkpoint

After the TDD gate passes, run through the checklist above for the current phase.
Every unchecked item is a blocker. Do not declare a phase complete with any unchecked items.

If a checkpoint item cannot be verified (e.g., data count is wrong), treat it as a
failing test — fix the root cause, do not mark it as done.
