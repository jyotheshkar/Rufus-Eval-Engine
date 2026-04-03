# Runs all 50 adversarial queries through the eval pipeline and prints a failure mode report

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.evaluation.pipeline import EvalPipeline


async def main(mock: bool) -> None:
    if mock:
        os.environ["USE_MOCK"] = "true"

    pipeline = EvalPipeline()
    print(f"Mock mode: {pipeline.rufus.use_mock}")
    print(f"Running 50 adversarial queries...\n{'=' * 60}")

    report = await pipeline.run_adversarial()

    print(f"\nResults by failure mode:")
    worst_cat = None
    worst_rate = -1.0

    for cat, stats in report["failure_summary"].items():
        avg = stats["avg_scores"]
        triggered = stats["triggered"]
        total = stats["count"]
        rate = stats["failure_rate"]

        # Find the lowest scoring dimension for this category
        dim_scores = {d: avg[d] for d in ("helpfulness", "accuracy", "hallucination", "safety")}
        worst_dim = min(dim_scores, key=dim_scores.get)

        print(
            f"  {cat:<25} avg {worst_dim}: {dim_scores[worst_dim]:.1f}/10  "
            f"| triggered: {triggered}/{total}  | failure rate: {rate:.0%}"
        )

        if rate > worst_rate:
            worst_rate = rate
            worst_cat = cat

    total_triggered = sum(s["triggered"] for s in report["failure_summary"].values())
    overall_rate = total_triggered / report["total"] if report["total"] else 0
    print(f"\nOverall adversarial failure rate: {overall_rate:.0%}")
    print(f"Worst category: {worst_cat}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Force USE_MOCK=true")
    args = parser.parse_args()
    asyncio.run(main(mock=args.mock))
