# Eval routes — paginated list and single eval result endpoints

import logging
from pathlib import Path
from typing import Optional

import aiosqlite
from fastapi import APIRouter, HTTPException, Query

from backend.models import EvalListResponse, EvalResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evals", tags=["evals"])

DB_PATH = Path(__file__).parent.parent / "data" / "eval_results.db"


def _row_to_eval_result(row: dict) -> EvalResult:
    """Convert a sqlite3.Row dict to an EvalResult model, casting INTEGER booleans."""
    return EvalResult(
        id=row["id"],
        timestamp=row["timestamp"],
        question_id=row["question_id"],
        question_text=row["question_text"],
        category=row["category"],
        difficulty=row["difficulty"],
        is_adversarial=bool(row["is_adversarial"]),
        adversarial_category=row["adversarial_category"],
        adversarial_triggered=bool(row["adversarial_triggered"]),
        failure_mode_detected=row["failure_mode_detected"],
        rufus_answer=row["rufus_answer"],
        score_helpfulness=row["score_helpfulness"],
        score_accuracy=row["score_accuracy"],
        score_hallucination=row["score_hallucination"],
        score_safety=row["score_safety"],
        score_overall=row["score_overall"],
        anomaly_flagged=bool(row["anomaly_flagged"]),
        anomaly_reason=row["anomaly_reason"],
    )


@router.get("", response_model=EvalListResponse)
async def list_evals(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(default=20, ge=1, le=100, description="Results per page"),
    category: Optional[str] = Query(default=None, description="Filter by product category"),
    is_adversarial: Optional[bool] = Query(default=None, description="Filter by adversarial flag"),
) -> EvalListResponse:
    """Return a paginated list of eval results with optional filters."""
    try:
        offset = (page - 1) * limit

        where_clauses: list[str] = []
        params: list = []

        if category is not None:
            where_clauses.append("category = ?")
            params.append(category)
        if is_adversarial is not None:
            where_clauses.append("is_adversarial = ?")
            params.append(int(is_adversarial))

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        async with aiosqlite.connect(str(DB_PATH)) as db:
            db.row_factory = aiosqlite.Row

            async with db.execute(
                f"SELECT COUNT(*) FROM eval_results {where_sql}", params
            ) as cursor:
                row = await cursor.fetchone()
                total = row[0] if row else 0

            async with db.execute(
                f"""
                SELECT * FROM eval_results {where_sql}
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                """,
                params + [limit, offset],
            ) as cursor:
                rows = await cursor.fetchall()

        results = [_row_to_eval_result(dict(row)) for row in rows]
        return EvalListResponse(total=total, page=page, results=results)

    except Exception as exc:
        logger.error("Failed to list evals: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to fetch eval results")


@router.get("/{eval_id}", response_model=EvalResult)
async def get_eval(eval_id: str) -> EvalResult:
    """Return a single eval result by its ID."""
    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM eval_results WHERE id = ?", (eval_id,)
            ) as cursor:
                row = await cursor.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail=f"Eval result '{eval_id}' not found")

        return _row_to_eval_result(dict(row))

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to get eval %s: %s", eval_id, exc)
        raise HTTPException(status_code=500, detail="Failed to fetch eval result")
