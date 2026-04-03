# Smoke-tests the full eval pipeline end-to-end with 3 questions using mock mode

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.evaluation.pipeline import EvalPipeline

TEST_QUESTIONS = [
    {
        "id": "q_001",
        "question": "What are the best wireless headphones under £100?",
        "category": "headphones",
        "difficulty": "easy",
    },
    {
        "id": "q_002",
        "question": "I need a lightweight laptop for university with long battery life",
        "category": "laptops",
        "difficulty": "medium",
    },
    {
        "id": "q_003",
        "question": "Compare smartwatches for fitness tracking under £200",
        "category": "smartwatches",
        "difficulty": "medium",
    },
]


async def main() -> None:
    pipeline = EvalPipeline()  # reads USE_MOCK from env
    print(f"Mock mode: {pipeline.rufus.use_mock}\n{'=' * 60}")

    for question in TEST_QUESTIONS:
        result = await pipeline.run_single(question)
        scores = result["scores"]
        print(f"\nQuestion [{result['question']['id']}]: {question['question']}")
        print(f"Products retrieved: {len(result['products_retrieved'])}")
        print(f"Answer ({len(result['rufus_answer'].split())} words): {result['rufus_answer'][:100]}...")
        print(f"Scores — helpfulness: {scores['helpfulness']} | accuracy: {scores['accuracy']} | "
              f"hallucination: {scores['hallucination']} | safety: {scores['safety']} | "
              f"overall: {scores['overall']}")
        print(f"Summary: {result['judge_reasoning']['summary']}")
        print("-" * 60)


if __name__ == "__main__":
    asyncio.run(main())
