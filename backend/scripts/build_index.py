# Builds the FAISS product index from products.json and saves it to data/faiss_index/

import json
import sys
import time
from pathlib import Path

# Allow imports from backend/
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.retrieval.faiss_retriever import FAISSRetriever

PRODUCTS_PATH = Path(__file__).parent.parent / "data" / "products.json"
INDEX_DIR = Path(__file__).parent.parent / "data" / "faiss_index"


def main() -> None:
    print(f"Loading {PRODUCTS_PATH.name}...")
    with open(PRODUCTS_PATH) as f:
        products = json.load(f)
    print(f"  {len(products)} products loaded.")

    start = time.time()

    retriever = FAISSRetriever(str(PRODUCTS_PATH))

    print("Embedding products and building FAISS index...")
    retriever.build_index()

    elapsed_embed = time.time() - start
    print(f"  Embedding done in {elapsed_embed:.1f}s")

    print(f"Saving index to {INDEX_DIR}...")
    retriever.save_index(str(INDEX_DIR))

    # Write embeddings back to products.json
    print("Writing embeddings back to products.json...")
    with open(PRODUCTS_PATH, "w") as f:
        json.dump(retriever.products, f, indent=2)

    elapsed_total = time.time() - start
    idx = retriever.index
    print(f"\nIndex built: {idx.ntotal} vectors, dimension {idx.d}")
    print(f"Saved to {INDEX_DIR}/")
    print(f"Done in {elapsed_total:.1f}s")


if __name__ == "__main__":
    main()
