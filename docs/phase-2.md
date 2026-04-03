# Phase 2 — FAISS Vector Store + Product Embeddings
**Status:** Complete
**Date completed:** 2026-04-03
**Built by:** Claude (claude-sonnet-4-6) + Jyothesh Karnam

---

## What this phase built

A search engine that can find the 5 most relevant products for any shopping question — in milliseconds. Every product was converted into a list of 384 numbers (called an embedding) that captures its meaning. Those numbers are stored in a FAISS index, which lets us instantly find the products whose numbers are closest to a question's numbers.

---

## Why this phase matters

Without retrieval, the Rufus agent has no products to talk about. Phase 3 (the shopping assistant) depends entirely on this layer to supply the right products before generating an answer. Good retrieval = good answers; bad retrieval = hallucinations.

---

## What was built

### FAISSRetriever class
**File:** `backend/retrieval/faiss_retriever.py`
**What it does:** Loads all 1000 products, converts each one to a text string (name + category + description + specs + tags), embeds that string into a 384-dimensional vector using the `all-MiniLM-L6-v2` model, then builds a FAISS flat index over all vectors. Given any shopping query, it embeds the query the same way and returns the 5 products whose vectors are closest.
**Key decisions made:**
- Used `IndexFlatL2` (exact search) — with only 1000 products this is fast enough and more accurate than approximate methods
- Used `all-MiniLM-L6-v2` from sentence-transformers — free, runs locally, no API cost, and good enough for product retrieval
- Index is saved to disk after building so subsequent runs load in under 1 second instead of rebuilding for 37 seconds

### Index builder script
**File:** `backend/scripts/build_index.py`
**What it does:** One-time script that loads products.json, builds the FAISS index, saves it to `backend/data/faiss_index/`, and writes the 384-float embedding vector back onto each product in products.json.
**Key decisions made:**
- Embeddings are written back to products.json so later phases (judge pipeline) can use them for similarity comparisons without re-embedding

### Smoke test script
**File:** `backend/scripts/test_retriever.py`
**What it does:** Loads the pre-built index and runs 5 representative shopping queries, printing the top 5 results for each with their L2 distance scores. Used to visually verify that retrieval is semantically sensible.

### FAISS index files (generated artifacts)
**Files:** `backend/data/faiss_index/products.index`, `backend/data/faiss_index/product_ids.json`
**What they are:** The serialised FAISS index (1.5 MB) and a JSON file mapping each index position to its product ID. Loading these takes under 1 second on subsequent runs.

---

## How data flows through this phase

1. `build_index.py` reads all 1000 products from `products.json`
2. Each product's name, category, description, specs, and tags are joined into one text string
3. `all-MiniLM-L6-v2` converts each string into a 384-dimensional float vector (the embedding)
4. All 1000 vectors are loaded into a FAISS `IndexFlatL2` index
5. The index is saved to `backend/data/faiss_index/products.index`
6. A position-to-product-ID map is saved to `product_ids.json`
7. Each product in `products.json` is updated with its embedding vector
8. At query time: `FAISSRetriever.search(query, k=5)` embeds the query, calls `index.search()`, and returns the 5 closest products with their L2 distances

---

## Tests written

| Test | What it checks | Why it matters |
|------|---------------|----------------|
| `test_search_returns_exactly_five_results` | Default search returns 5 products | Rufus agent always expects exactly 5 candidates |
| `test_search_results_sorted_by_distance` | L2 distances are non-decreasing | Most relevant product is always first |
| `test_search_returns_one_result_when_k_is_one` | k parameter is respected | Pipeline can request different numbers of results |
| `test_product_embeddings_are_non_zero` | Embedding vectors are non-zero | sentence-transformers ran correctly, not returning empty vectors |
| `test_search_raises_if_index_not_loaded` | RuntimeError when no index | Fails loudly rather than silently returning wrong results |
| `test_index_files_exist_on_disk` | Index files present after build | Index persists between runs — no rebuild needed |

---

## Checkpoint verification

- ✓ `backend/retrieval/faiss_retriever.py` fully implemented
- ✓ FAISS index built from all 1000 products
- ✓ `products.json` updated with embeddings for all products
- ✓ Top-5 retrieval returns semantically relevant results
- ✓ Retrieval tested with 5 sample queries
- ✓ Index build script runs cleanly (no API calls)
- ✓ `docs/phase-2.md` generated

---

## Known limitations

The FAISS index is built once and saved statically. If products.json changes (e.g. new products added), `build_index.py` must be re-run manually. There is no automatic incremental update.

---

## What comes next

Phase 3 builds the Rufus agent — it will call `FAISSRetriever.search()` to get 5 candidate products, then pass them to Claude Haiku to generate a shopping answer.
