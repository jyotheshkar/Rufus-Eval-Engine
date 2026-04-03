# Smoke-tests the Rufus agent with 3 queries using the FAISS retriever and mock mode

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.agents.rufus_agent import RufusAgent
from backend.retrieval.faiss_retriever import FAISSRetriever

PRODUCTS_PATH = Path(__file__).parent.parent / "data" / "products.json"
INDEX_DIR = Path(__file__).parent.parent / "data" / "faiss_index"

TEST_CASES = [
    "What are the best wireless headphones under £100?",
    "I need a laptop for university — lightweight and long battery",
    "Compare smartwatches for fitness tracking",
]


async def main() -> None:
    retriever = FAISSRetriever(str(PRODUCTS_PATH))
    retriever.load_index(str(INDEX_DIR))

    agent = RufusAgent()  # reads USE_MOCK from .env
    print(f"Mock mode: {agent.use_mock}\n{'=' * 60}")

    for query in TEST_CASES:
        products = retriever.search(query, k=5)
        result = await agent.generate_answer(query, products)

        word_count = len(result["answer"].split())
        print(f"\nQuery: {query}")
        print(f"Model: {result['model']} | Words: {word_count} | Products used: {len(result['products_used'])}")
        print(f"Answer:\n{result['answer']}")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())
