# Phase 2 Progress — FAISS Vector Store + Product Embeddings
**Completed:** 2026-04-03
**Phase status:** Complete

---

## What was done
- Verified and confirmed `faiss_retriever.py` scaffold from Phase 1 was complete and correct
- Fixed `requirements.txt`: `faiss-cpu` bumped from 1.7.4 → 1.8.0 (old version no longer on PyPI), `sentence-transformers` bumped from 2.5.1 → >=3.0.0 (broken in Python 3.12)
- Ran `build_index.py` — embedded all 1000 products and built FAISS index in 37.8s
- Ran `test_retriever.py` — all 5 smoke-test queries returned semantically correct results
- Created `backend/tests/` directory with `__init__.py`
- Wrote and ran 6 pytest tests — all passing

## Files created or modified
| File | Change |
|------|--------|
| `backend/retrieval/faiss_retriever.py` | Verified complete (scaffolded in Phase 1) |
| `backend/scripts/build_index.py` | Verified complete (scaffolded in Phase 1) |
| `backend/scripts/test_retriever.py` | Verified complete (scaffolded in Phase 1) |
| `backend/requirements.txt` | Modified — updated faiss-cpu and sentence-transformers versions |
| `backend/data/faiss_index/products.index` | Created — FAISS index (1.5 MB, 1000 vectors) |
| `backend/data/faiss_index/product_ids.json` | Created — position-to-product-ID map |
| `backend/data/products.json` | Modified — embedding field added to all 1000 products |
| `backend/tests/__init__.py` | Created — makes tests a package |
| `backend/tests/test_phase2.py` | Created — 6 pytest tests for retriever |
| `docs/phase-2.md` | Created — phase documentation |

## Test results
- Tests written: 6
- Tests passed: 6
- Tests failed: 0

## Checkpoint status
All checkpoint criteria met: Yes

## Issues encountered
- `faiss-cpu==1.7.4` no longer exists on PyPI — updated to `1.8.0`
- `sentence-transformers==2.5.1` has a broken internal module in Python 3.12 environments — updated to `>=3.0.0`
- `pytest` was not installed in the environment — installed it
- `backend/tests/` directory did not exist — created with `__init__.py`

## Notes for next phase
- The FAISS index is now at `backend/data/faiss_index/` — Phase 3 (Rufus agent) should call `FAISSRetriever.load_index()` on startup, not `build_index()`
- Embeddings are on every product in `products.json` — available for judge similarity comparisons in Phase 4
- `USE_MOCK` is irrelevant for Phase 2 (no API calls); Phase 3 will reintroduce the mock guard
