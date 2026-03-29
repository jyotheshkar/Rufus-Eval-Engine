# Phase 2 — FAISS Vector Store + Product Embeddings

## Goal
Build the retrieval layer. Convert all 1000 products into vector embeddings,
store them in a FAISS index, and expose a clean retriever class that returns
the top-k most relevant products for any shopping query.

---

## Step 1 — Build faiss_retriever.py

File: backend/retrieval/faiss_retriever.py

### What this file does:
- Loads products.json on startup
- Creates embeddings for each product using sentence-transformers (free, no API cost)
- Builds a FAISS index over the embeddings
- Exposes a search(query, k=5) method that returns the top-k products

### Embedding strategy:
Embed a text representation of each product, not just the name.
Combine: name + category + description + key specs into one string.

Example:
```python
def product_to_text(product):
    specs = " ".join([f"{k}: {v}" for k, v in product["specs"].items()])
    return f"{product['name']} {product['category']} {product['description']} {specs}"
```

### Class interface:
```python
class FAISSRetriever:
    def __init__(self, products_path: str):
        # load products, build index on init
        pass

    def search(self, query: str, k: int = 5) -> list[dict]:
        # embed query, search index, return top-k products
        pass

    def save_index(self, path: str):
        # save FAISS index to disk so we don't rebuild every time
        pass

    def load_index(self, path: str):
        # load pre-built index from disk
        pass
```

### Model to use:
sentence-transformers: "all-MiniLM-L6-v2"
- Fast, small, free
- Good enough for product retrieval
- No API cost

### Index type:
Use faiss.IndexFlatL2 — simple and accurate for 1000 products.
No need for approximate methods at this scale.

---

## Step 2 — Save index to disk

After building the index, save it to:
backend/data/faiss_index/products.index
backend/data/faiss_index/product_ids.json  (maps index position to product id)

On subsequent runs, load from disk instead of rebuilding.
Check if index file exists first. If yes, load. If no, build and save.

---

## Step 3 — Build index builder script

File: backend/scripts/build_index.py

```bash
python backend/scripts/build_index.py
```

This script:
1. Loads products.json
2. Builds FAISS index
3. Saves to backend/data/faiss_index/
4. Prints timing and index stats

Expected output:
```
Loading 1000 products...
Embedding products... (this takes ~30 seconds first time)
Building FAISS index...
Index built: 1000 vectors, dimension 384
Saved to backend/data/faiss_index/
Done in 45.2s
```

---

## Step 4 — Write retriever tests

File: backend/scripts/test_retriever.py

Test these queries and print the top 5 results for each:

```python
test_queries = [
    "best wireless headphones under £100",
    "lightweight laptop for students",
    "waterproof smartwatch for swimming",
    "gaming mouse with RGB lighting",
    "4K monitor for graphic design"
]
```

Expected output format:
```
Query: best wireless headphones under £100
1. Sony WH-CH520 (headphones) - £49.99 - Score: 0.92
2. JBL Tune 510BT (headphones) - £39.99 - Score: 0.89
3. Anker Soundcore Q20 (headphones) - £35.99 - Score: 0.87
4. Jabra Evolve2 (headphones) - £89.99 - Score: 0.84
5. Sennheiser HD 350BT (headphones) - £79.99 - Score: 0.81
```

---

## Step 5 — Add embeddings back to products.json

After building the index, update each product in products.json to include
its embedding vector. This is used later for similarity comparisons in the
judge pipeline.

```python
product["embedding"] = embedding_vector.tolist()
```

---

## Step 6 — Verify phase 2

```bash
# Build the index
python backend/scripts/build_index.py

# Test retrieval
python backend/scripts/test_retriever.py

# Check index files exist
ls backend/data/faiss_index/
```

## Phase 2 complete when:
- faiss_retriever.py is fully implemented with save/load
- FAISS index built and saved to disk
- test_retriever.py returns sensible results for all 5 test queries
- No API calls made in this phase (sentence-transformers runs locally)
- Zero API cost for this entire phase
