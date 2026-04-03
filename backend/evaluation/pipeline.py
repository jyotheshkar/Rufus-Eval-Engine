# Evaluation pipeline — orchestrates retrieval, answer generation, judging, and storage

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from backend.agents.judge_agent import JudgeAgent
from backend.agents.rufus_agent import RufusAgent
from backend.evaluation.anomaly import AnomalyDetector, init_db
from backend.retrieval.faiss_retriever import FAISSRetriever

logger = logging.getLogger(__name__)

PRODUCTS_PATH = Path(__file__).parent.parent / "data" / "products.json"
INDEX_DIR = Path(__file__).parent.parent / "data" / "faiss_index"
ADVERSARIAL_PATH = Path(__file__).parent.parent / "data" / "adversarial.json"


class EvalPipeline:
    """Runs the full evaluation loop: retrieve → answer → judge → result."""

    def __init__(self, use_mock: bool | None = None, db_path: str | None = None) -> None:
        self.retriever = FAISSRetriever(str(PRODUCTS_PATH))
        self.retriever.load_index(str(INDEX_DIR))
        self.rufus = RufusAgent(use_mock=use_mock)
        self.judge = JudgeAgent(use_mock=use_mock)
        self.anomaly = AnomalyDetector(db_path=db_path)
        logger.info("EvalPipeline ready — use_mock=%s", self.rufus.use_mock)

    async def run_single(
        self,
        question: dict,
        is_adversarial: bool = False,
        adversarial_category: str | None = None,
    ) -> dict:
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

        judge_result = await self.judge.score(query, products, answer, adversarial_category=adversarial_category)

        result = {
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
            "adversarial_category": adversarial_category,
            "adversarial_triggered": judge_result.get("adversarial_triggered", False),
            "failure_mode_detected": judge_result.get("failure_mode_detected", "none"),
            "usage": rufus_result.get("usage", {}),
            "anomaly_flagged": False,
            "anomaly_reason": "",
        }

        result = await self.anomaly.check(result)
        await self.anomaly.save_result(result)
        return result

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

    async def run_adversarial(self, delay: float = 0.0) -> dict:
        """Run all 50 adversarial queries and return a failure mode summary.

        Returns a dict with total count, per-result list, and failure_summary
        broken down by category with average scores for the targeted dimension.
        """
        with open(ADVERSARIAL_PATH) as f:
            adversarial_queries = json.load(f)

        results = []
        for i, query in enumerate(adversarial_queries):
            logger.info("Adversarial %d/%d: %s", i + 1, len(adversarial_queries), query["id"])
            result = await self.run_single(
                question=query,
                is_adversarial=True,
                adversarial_category=query.get("category"),
            )
            results.append(result)
            if delay > 0 and i < len(adversarial_queries) - 1:
                await asyncio.sleep(delay)

        failure_summary = self._build_failure_summary(results)
        return {
            "total": len(results),
            "results": results,
            "failure_summary": failure_summary,
        }

    def _build_failure_summary(self, results: list[dict]) -> dict:
        """Aggregate results by adversarial category, computing avg scores per dimension."""
        categories: dict[str, list[dict]] = {}
        for r in results:
            cat = r.get("adversarial_category") or "unknown"
            categories.setdefault(cat, []).append(r)

        summary = {}
        for cat, cat_results in categories.items():
            scores_by_dim: dict[str, list[float]] = {
                "helpfulness": [], "accuracy": [], "hallucination": [], "safety": [], "overall": []
            }
            triggered_count = 0
            for r in cat_results:
                for dim in scores_by_dim:
                    scores_by_dim[dim].append(float(r["scores"].get(dim, 0)))
                if r.get("adversarial_triggered"):
                    triggered_count += 1

            summary[cat] = {
                "count": len(cat_results),
                "triggered": triggered_count,
                "failure_rate": round(triggered_count / len(cat_results), 2) if cat_results else 0.0,
                "avg_scores": {
                    dim: round(sum(v) / len(v), 2) if v else 0.0
                    for dim, v in scores_by_dim.items()
                },
            }
        return summary
