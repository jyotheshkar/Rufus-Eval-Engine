# Stats routes — health check, overview, category breakdown, trend, and anomaly endpoints

import logging
from pathlib import Path

import aiosqlite
from fastapi import APIRouter, HTTPException, Query

from backend.models import AnomalyItem, CategoryStat, HealthResponse, OverviewStats, TrendPoint

logger = logging.getLogger(__name__)

router = APIRouter(tags=["stats"])

DB_PATH = Path(__file__).parent.parent / "data" / "eval_results.db"


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return service health and basic DB stats."""
    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            async with db.execute("SELECT COUNT(*) FROM eval_results") as cursor:
                row = await cursor.fetchone()
                total = row[0] if row else 0

            async with db.execute(
                "SELECT timestamp FROM eval_runs ORDER BY timestamp DESC LIMIT 1"
            ) as cursor:
                run_row = await cursor.fetchone()
                last_run = run_row[0] if run_row else None

        return HealthResponse(status="ok", total_evals=total, last_run=last_run)

    except Exception as exc:
        logger.error("Health check failed: %s", exc)
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/stats/overview", response_model=OverviewStats)
async def stats_overview() -> OverviewStats:
    """Return aggregate statistics across all eval results."""
    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            async with db.execute(
                """
                SELECT
                    COUNT(*) AS total_evals,
                    COALESCE(AVG(score_overall), 0.0) AS avg_overall,
                    COALESCE(AVG(score_helpfulness), 0.0) AS avg_helpfulness,
                    COALESCE(AVG(score_accuracy), 0.0) AS avg_accuracy,
                    COALESCE(AVG(score_hallucination), 0.0) AS avg_hallucination,
                    COALESCE(AVG(score_safety), 0.0) AS avg_safety,
                    SUM(anomaly_flagged) AS anomaly_count
                FROM eval_results
                """
            ) as cursor:
                row = await cursor.fetchone()

            total_evals = row[0] if row else 0
            avg_overall = round(row[1], 2) if row else 0.0
            avg_helpfulness = round(row[2], 2) if row else 0.0
            avg_accuracy = round(row[3], 2) if row else 0.0
            avg_hallucination = round(row[4], 2) if row else 0.0
            avg_safety = round(row[5], 2) if row else 0.0
            anomaly_count = int(row[6] or 0) if row else 0

            # Find adversarial category with highest failure rate
            worst_category = "none"
            if total_evals > 0:
                async with db.execute(
                    """
                    SELECT
                        adversarial_category,
                        COUNT(*) AS cnt,
                        SUM(adversarial_triggered) AS triggered
                    FROM eval_results
                    WHERE is_adversarial = 1 AND adversarial_category IS NOT NULL
                    GROUP BY adversarial_category
                    HAVING cnt > 0
                    ORDER BY CAST(triggered AS REAL) / cnt DESC
                    LIMIT 1
                    """
                ) as cursor:
                    adv_row = await cursor.fetchone()
                    if adv_row and adv_row[0]:
                        worst_category = adv_row[0]

        return OverviewStats(
            total_evals=total_evals,
            avg_overall=avg_overall,
            avg_helpfulness=avg_helpfulness,
            avg_accuracy=avg_accuracy,
            avg_hallucination=avg_hallucination,
            avg_safety=avg_safety,
            anomaly_count=anomaly_count,
            worst_category=worst_category,
        )

    except Exception as exc:
        logger.error("Failed to get overview stats: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch overview stats")


@router.get("/stats/by-category", response_model=list[CategoryStat])
async def stats_by_category() -> list[CategoryStat]:
    """Return average scores per product category, sorted by avg_overall descending."""
    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            async with db.execute(
                """
                SELECT
                    category,
                    ROUND(AVG(score_overall), 2) AS avg_overall,
                    COUNT(*) AS count
                FROM eval_results
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY avg_overall DESC
                """
            ) as cursor:
                rows = await cursor.fetchall()

        return [
            CategoryStat(category=row[0], avg_overall=row[1], count=row[2])
            for row in rows
        ]

    except Exception as exc:
        logger.error("Failed to get by-category stats: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch category stats")


@router.get("/stats/trend", response_model=list[TrendPoint])
async def stats_trend(
    days: int = Query(default=7, ge=1, le=90, description="Number of days to include in trend")
) -> list[TrendPoint]:
    """Return daily average overall scores for the past N days."""
    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            async with db.execute(
                """
                SELECT
                    DATE(timestamp) AS date,
                    ROUND(AVG(score_overall), 2) AS avg_overall
                FROM eval_results
                WHERE timestamp >= DATE('now', ? || ' days')
                GROUP BY DATE(timestamp)
                ORDER BY date ASC
                """,
                (f"-{days}",),
            ) as cursor:
                rows = await cursor.fetchall()

        return [TrendPoint(date=row[0], avg_overall=row[1]) for row in rows]

    except Exception as exc:
        logger.error("Failed to get trend stats: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch trend stats")


@router.get("/stats/anomalies", response_model=list[AnomalyItem])
async def stats_anomalies() -> list[AnomalyItem]:
    """Return all anomaly-flagged eval results ordered by timestamp descending."""
    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            async with db.execute(
                """
                SELECT id, timestamp, question_text, score_overall, anomaly_reason
                FROM eval_results
                WHERE anomaly_flagged = 1
                ORDER BY timestamp DESC
                """
            ) as cursor:
                rows = await cursor.fetchall()

        return [
            AnomalyItem(
                eval_id=row[0],
                timestamp=row[1],
                question_text=row[2],
                score_overall=row[3],
                anomaly_reason=row[4] or "",
            )
            for row in rows
        ]

    except Exception as exc:
        logger.error("Failed to get anomalies: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch anomaly stats")
