# Run evaluation — executes a full eval pass over the question bank and saves to SQLite

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.evaluation.anomaly import init_db
from backend.evaluation.pipeline import EvalPipeline

QUESTIONS_PATH = Path(__file__).parent.parent / "data" / "questions.json"


async def main(mock: bool, limit: int) -> None:
    if mock:
        os.environ["USE_MOCK"] = "true"

    await init_db()

    with open(QUESTIONS_PATH) as f:
        all_questions = json.load(f)

    questions = all_questions[:limit]
    pipeline = EvalPipeline()

    print(f"Mock mode: {pipeline.rufus.use_mock}")
    print(f"Running {len(questions)} questions...\n{'=' * 60}")

    results = await pipeline.run_batch(questions, delay=0.0)

    anomaly_count = sum(1 for r in results if r.get("anomaly_flagged"))
    scores = [r["scores"]["overall"] for r in results]
    avg = sum(scores) / len(scores) if scores else 0.0

    run_id = str(uuid4())
    run_summary = {
        "id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": "standard",
        "total_questions": len(results),
        "avg_overall": round(avg, 2),
        "avg_helpfulness": round(sum(r["scores"]["helpfulness"] for r in results) / len(results), 2),
        "avg_accuracy": round(sum(r["scores"]["accuracy"] for r in results) / len(results), 2),
        "avg_hallucination": round(sum(r["scores"]["hallucination"] for r in results) / len(results), 2),
        "avg_safety": round(sum(r["scores"]["safety"] for r in results) / len(results), 2),
    }
    await pipeline.anomaly.save_run(run_summary)

    print(f"\nResults saved to SQLite.")
    print(f"Questions evaluated: {len(results)}")
    print(f"Avg overall score:   {avg:.2f}/10")
    print(f"Anomalies flagged:   {anomaly_count}")
    print(f"Run ID: {run_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Force USE_MOCK=true")
    parser.add_argument("--limit", type=int, default=10, help="Number of questions to run")
    args = parser.parse_args()
    asyncio.run(main(mock=args.mock, limit=args.limit))
