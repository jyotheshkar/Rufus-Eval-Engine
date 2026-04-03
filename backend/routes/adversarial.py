# Adversarial routes — summary of adversarial test results grouped by failure mode category

import logging
from pathlib import Path

import aiosqlite
from fastapi import APIRouter, HTTPException

from backend.models import AdversarialCategoryStat, AdversarialSummary

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/adversarial", tags=["adversarial"])

DB_PATH = Path(__file__).parent.parent / "data" / "eval_results.db"


@router.get("/summary", response_model=AdversarialSummary)
async def adversarial_summary() -> AdversarialSummary:
    """Return adversarial test results grouped by failure mode category."""
    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM eval_results WHERE is_adversarial = 1"
            ) as cursor:
                row = await cursor.fetchone()
                total = row[0] if row else 0

            async with db.execute(
                """
                SELECT
                    COALESCE(adversarial_category, 'unknown') AS category,
                    COUNT(*) AS count,
                    SUM(adversarial_triggered) AS triggered,
                    ROUND(AVG(score_overall), 2) AS avg_overall
                FROM eval_results
                WHERE is_adversarial = 1
                GROUP BY adversarial_category
                ORDER BY category ASC
                """
            ) as cursor:
                rows = await cursor.fetchall()

        by_category = [
            AdversarialCategoryStat(
                category=row[0],
                count=row[1],
                triggered=int(row[2] or 0),
                failure_rate=round(int(row[2] or 0) / row[1], 2) if row[1] > 0 else 0.0,
                avg_overall=row[3] if row[3] is not None else 0.0,
            )
            for row in rows
        ]

        return AdversarialSummary(total=total, by_category=by_category)

    except Exception as exc:
        logger.error("Failed to get adversarial summary: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch adversarial summary")
