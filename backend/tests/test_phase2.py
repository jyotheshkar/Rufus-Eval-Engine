# Phase 2 tests: verifies FAISS retriever behaviour using the pre-built index

import json
import sys
from pathlib import Path

import pytest

# Allow imports from the repo root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.retrieval.faiss_retriever import FAISSRetriever

PRODUCTS_PATH = str(Path(__file__).parent.parent / "data" / "products.json")
INDEX_DIR = str(Path(__file__).parent.parent / "data" / "faiss_index")
INDEX_FILE = Path(__file__).parent.parent / "data" / "faiss_index" / "products.index"
IDS_FILE = Path(__file__).parent.parent / "data" / "faiss_index" / "product_ids.json"


# ---------------------------------------------------------------------------
# Module-scoped fixture: load the retriever once for all tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def retriever() -> FAISSRetriever:
    """Return a FAISSRetriever with the pre-built index already loaded."""
    r = FAISSRetriever(PRODUCTS_PATH)
    r.load_index(INDEX_DIR)
    return r


# ---------------------------------------------------------------------------
# Test 1 — retriever returns exactly 5 results for a valid query
# ---------------------------------------------------------------------------

def test_search_returns_exactly_five_results(retriever: FAISSRetriever) -> None:
    results = retriever.search("wireless headphones for commuting", k=5)
    assert len(results) == 5, f"Expected 5 results, got {len(results)}"


# ---------------------------------------------------------------------------
# Test 2 — results are sorted by ascending L2 distance (most similar first)
# ---------------------------------------------------------------------------

def test_search_results_sorted_by_distance(retriever: FAISSRetriever) -> None:
    results = retriever.search("gaming laptop with RTX graphics card", k=5)
    assert len(results) >= 2, "Need at least 2 results to check ordering"
    scores = [r["_score"] for r in results]
    assert scores == sorted(scores), (
        f"Results not sorted by ascending L2 distance: {scores}"
    )


# ---------------------------------------------------------------------------
# Test 3 — retriever handles k=1 correctly (returns exactly 1 result)
# ---------------------------------------------------------------------------

def test_search_returns_one_result_when_k_is_one(retriever: FAISSRetriever) -> None:
    results = retriever.search("smartwatch fitness tracker", k=1)
    assert len(results) == 1, f"Expected 1 result for k=1, got {len(results)}"
    assert "_score" in results[0], "Result must include _score field"


# ---------------------------------------------------------------------------
# Test 4 — embeddings in products.json are non-zero (build_index sanity check)
# ---------------------------------------------------------------------------

def test_product_embeddings_are_non_zero() -> None:
    with open(PRODUCTS_PATH) as f:
        products = json.load(f)
    for product in products[:10]:  # check first 10 products as a representative sample
        assert "embedding" in product, f"Product {product['id']} missing embedding field"
        embedding = product["embedding"]
        assert len(embedding) == 384, (
            f"Expected embedding dimension 384, got {len(embedding)} for {product['id']}"
        )
        assert any(v != 0.0 for v in embedding), (
            f"Embedding for {product['id']} is all zeros — model did not run"
        )


# ---------------------------------------------------------------------------
# Test 5 — retriever raises RuntimeError if search called before index is loaded
# ---------------------------------------------------------------------------

def test_search_raises_if_index_not_loaded() -> None:
    unloaded = FAISSRetriever(PRODUCTS_PATH)
    # Do NOT call load_index or build_index — index should be None
    with pytest.raises(RuntimeError, match="Index not built or loaded"):
        unloaded.search("any query")


# ---------------------------------------------------------------------------
# Test 6 — index files exist on disk after build_index ran
# ---------------------------------------------------------------------------

def test_index_files_exist_on_disk() -> None:
    assert INDEX_FILE.exists(), f"FAISS index file not found: {INDEX_FILE}"
    assert IDS_FILE.exists(), f"product_ids.json not found: {IDS_FILE}"
    # Sanity-check that product_ids.json has 1000 entries
    with open(IDS_FILE) as f:
        ids = json.load(f)
    assert len(ids) == 1000, f"Expected 1000 product IDs, got {len(ids)}"
