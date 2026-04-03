# Smoke-tests the FAISS retriever by running 5 representative queries and printing top-5 results

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.retrieval.faiss_retriever import FAISSRetriever

PRODUCTS_PATH = Path(__file__).parent.parent / "data" / "products.json"
INDEX_DIR = Path(__file__).parent.parent / "data" / "faiss_index"

TEST_QUERIES = [
    "best wireless headphones under £100",
    "lightweight laptop for students",
    "waterproof smartwatch for swimming",
    "gaming mouse with RGB lighting",
    "4K monitor for graphic design",
]


def main() -> None:
    retriever = FAISSRetriever(str(PRODUCTS_PATH))
    retriever.load_index(str(INDEX_DIR))

    for query in TEST_QUERIES:
        print(f"\nQuery: {query}")
        results = retriever.search(query, k=5)
        for i, product in enumerate(results, 1):
            score = product.get("_score", 0.0)
            print(
                f"  {i}. {product['name']} ({product['category']}) "
                f"- £{product['price']:.2f} - L2 dist: {score:.4f}"
            )


if __name__ == "__main__":
    main()
