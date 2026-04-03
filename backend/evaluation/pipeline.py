# Evaluation pipeline — orchestrates retrieval, answer generation, judging, and storage

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from backend.agents.judge_agent import JudgeAgent
from backend.agents.rufus_agent import RufusAgent
from backend.retrieval.faiss_retriever import FAISSRetriever

logger = logging.getLogger(__name__)

PRODUCTS_PATH = Path(__file__).parent.parent / "data" / "products.json"
INDEX_DIR = Path(__file__).parent.parent / "data" / "faiss_index"


class EvalPipeline:
    """Runs the full evaluation loop: retrieve → answer → judge → result."""

    def __init__(self, use_mock: bool | None = None) -> None:
        self.retriever = FAISSRetriever(str(PRODUCTS_PATH))
        self.retriever.load_index(str(INDEX_DIR))
        self.rufus = RufusAgent(use_mock=use_mock)
        self.judge = JudgeAgent(use_mock=use_mock)
        logger.info(
            "EvalPipeline ready — use_mock=%s", self.rufus.use_mock
        )

    async def run_single(self, question: dict, is_adversarial: bool = False) -> dict:
        """Run one full eval: retrieve → answer → judge.

        Args:
            question: A question dict with at least 'id' and 'question' keys.
            is_adversarial: Whether this question is from the adversarial suite.

        Returns:
            A full eval result dict.
        """
        query = question["question"]

        products = self.retriever.search(query, k=5)
        logger.debug("Retrieved %d products for question %s", len(products), question["id"])

        rufus_result = await self.rufus.generate_answer(query, products)
        answer = rufus_result["answer"]

        judge_result = await self.judge.score(query, products, answer)

        return {
            "eval_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "question": question,
            "products_retrieved": [
                {"id": p["id"], "name": p["name"], "category": p["category"]}
                for p in products
            ],
            "rufus_answer": answer,
            "rufus_model": rufus_result["model"],
            "scores": {
                "helpfulness": judge_result["helpfulness"]["score"],
                "accuracy": judge_result["accuracy"]["score"],
                "hallucination": judge_result["hallucination"]["score"],
                "safety": judge_result["safety"]["score"],
                "overall": judge_result.get("overall", 0.0),
            },
            "judge_reasoning": {
                "helpfulness": judge_result["helpfulness"]["reasoning"],
                "accuracy": judge_result["accuracy"]["reasoning"],
                "hallucination": judge_result["hallucination"]["reasoning"],
                "safety": judge_result["safety"]["reasoning"],
                "summary": judge_result.get("summary", ""),
            },
            "judge_model": judge_result.get("model", "unknown"),
            "is_adversarial": is_adversarial,
            "usage": rufus_result.get("usage", {}),
        }

    async def run_batch(
        self,
        questions: list[dict],
        mode: str = "standard",
        delay: float = 0.1,
    ) -> list[dict]:
        """Run a batch of questions through the pipeline.

        Args:
            questions: List of question dicts.
            mode: "standard" or "adversarial".
            delay: Seconds to wait between calls (avoids rate limits in live mode).

        Returns:
            List of eval result dicts.
        """
        is_adversarial = mode == "adversarial"
        results = []
        for i, question in enumerate(questions):
            logger.info("Running question %d/%d: %s", i + 1, len(questions), question["id"])
            result = await self.run_single(question, is_adversarial=is_adversarial)
            results.append(result)
            if delay > 0 and i < len(questions) - 1:
                await asyncio.sleep(delay)
        return results
