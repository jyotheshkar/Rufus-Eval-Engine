# Anomaly detector — flags score drops vs rolling average baseline

import logging
import math
from pathlib import Path

import aiosqlite

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "data" / "eval_results.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS eval_results (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    question_id TEXT,
    question_text TEXT,
    category TEXT,
    difficulty TEXT,
    is_adversarial INTEGER,
    adversarial_category TEXT,
    adversarial_triggered INTEGER DEFAULT 0,
    failure_mode_detected TEXT,
    rufus_answer TEXT,
    score_helpfulness REAL,
    score_accuracy REAL,
    score_hallucination REAL,
    score_safety REAL,
    score_overall REAL,
    anomaly_flagged INTEGER DEFAULT 0,
    anomaly_reason TEXT
);

CREATE TABLE IF NOT EXISTS eval_runs (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    mode TEXT,
    total_questions INTEGER,
    avg_overall REAL,
    avg_helpfulness REAL,
    avg_accuracy REAL,
    avg_hallucination REAL,
    avg_safety REAL
);
"""


async def init_db(db_path: str | None = None) -> None:
    """Create the SQLite database and tables if they don't exist."""
    path = db_path or str(DB_PATH)
    async with aiosqlite.connect(path) as db:
        await db.executescript(SCHEMA)
        await db.commit()
    logger.info("Database initialised at %s", path)


class AnomalyDetector:
    """Flags eval results whose overall score drops >1.5 std devs below the rolling category mean."""

    def __init__(self, db_path: str | None = None, window: int = 20) -> None:
        self.db_path = db_path or str(DB_PATH)
        self.window = window

    async def check(self, result: dict) -> dict:
        """Check a result for anomaly and return it with anomaly_flagged and anomaly_reason set.

        Compares result's overall score against rolling mean for its category.
        Flags if score is more than 1.5 std devs below the mean.
        """
        category = result.get("question", {}).get("category", "unknown")
        current_score = float(result["scores"]["overall"])

        stats = await self.get_rolling_stats(category)
        result = dict(result)

        if stats["count"] < 2:
            result["anomaly_flagged"] = False
            result["anomaly_reason"] = ""
            return result

        mean = stats["mean_overall"]
        std = stats["std_overall"]

        drop = mean - current_score
        # Flag if drop exceeds 1.5 std devs, or if std is 0 and drop is large (>2.0 points)
        is_anomaly = (std > 0 and drop > 1.5 * std) or (std == 0 and drop > 2.0)

        if is_anomaly:
            deviation_str = f"{(drop / std):.1f} std devs" if std > 0 else f"{drop:.1f} points"
            result["anomaly_flagged"] = True
            result["anomaly_reason"] = (
                f"Score {current_score:.1f} is {deviation_str} "
                f"below category mean {mean:.1f} (category={category})"
            )
            logger.warning("Anomaly flagged: %s", result["anomaly_reason"])
        else:
            result["anomaly_flagged"] = False
            result["anomaly_reason"] = ""

        return result

    async def get_rolling_stats(self, category: str) -> dict:
        """Return mean and std dev of overall score for the last N results in this category."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                """
                SELECT score_overall FROM eval_results
                WHERE category = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (category, self.window),
            ) as cursor:
                rows = await cursor.fetchall()

        scores = [row[0] for row in rows if row[0] is not None]
        if not scores:
            return {"count": 0, "mean_overall": 0.0, "std_overall": 0.0}

        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std = math.sqrt(variance)

        return {"count": len(scores), "mean_overall": round(mean, 4), "std_overall": round(std, 4)}

    async def save_result(self, result: dict) -> None:
        """Persist a single eval result to the database."""
        question = result.get("question", {})
        scores = result.get("scores", {})

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO eval_results (
                    id, timestamp, question_id, question_text, category, difficulty,
                    is_adversarial, adversarial_category, adversarial_triggered,
                    failure_mode_detected, rufus_answer,
                    score_helpfulness, score_accuracy, score_hallucination,
                    score_safety, score_overall,
                    anomaly_flagged, anomaly_reason
                ) VALUES (
                    ?, ?, ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?
                )
                """,
                (
                    result["eval_id"],
                    result["timestamp"],
                    question.get("id", ""),
                    question.get("question", ""),
                    question.get("category", ""),
                    question.get("difficulty", ""),
                    int(result.get("is_adversarial", False)),
                    result.get("adversarial_category"),
                    int(result.get("adversarial_triggered", False)),
                    result.get("failure_mode_detected", "none"),
                    result.get("rufus_answer", ""),
                    scores.get("helpfulness"),
                    scores.get("accuracy"),
                    scores.get("hallucination"),
                    scores.get("safety"),
                    scores.get("overall"),
                    int(result.get("anomaly_flagged", False)),
                    result.get("anomaly_reason", ""),
                ),
            )
            await db.commit()
        logger.debug("Saved eval result %s to DB", result["eval_id"])

    async def save_run(self, run: dict) -> None:
        """Persist an eval run summary to the database."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO eval_runs (
                    id, timestamp, mode, total_questions,
                    avg_overall, avg_helpfulness, avg_accuracy,
                    avg_hallucination, avg_safety
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run["id"],
                    run["timestamp"],
                    run["mode"],
                    run["total_questions"],
                    run["avg_overall"],
                    run["avg_helpfulness"],
                    run["avg_accuracy"],
                    run["avg_hallucination"],
                    run["avg_safety"],
                ),
            )
            await db.commit()
        logger.debug("Saved eval run %s to DB", run["id"])
