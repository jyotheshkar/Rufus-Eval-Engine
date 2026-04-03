# Tests for anomaly detection and SQLite storage (Phase 6)

import asyncio
import os
import tempfile

import pytest

from backend.evaluation.anomaly import AnomalyDetector, init_db
from backend.evaluation.pipeline import EvalPipeline

SAMPLE_QUESTION = {
    "id": "q_001",
    "question": "Best wireless headphones under £100?",
    "category": "headphones",
    "difficulty": "easy",
}


def make_result(score: float, category: str = "headphones") -> dict:
    """Build a minimal eval result dict with the given overall score."""
    return {
        "eval_id": f"test_{score}",
        "timestamp": "2026-04-03T00:00:00+00:00",
        "question": {"id": "q_001", "question": "test", "category": category, "difficulty": "easy"},
        "products_retrieved": [],
        "rufus_answer": "test answer",
        "rufus_model": "mock",
        "scores": {
            "helpfulness": score,
            "accuracy": score,
            "hallucination": score,
            "safety": score,
            "overall": score,
        },
        "judge_reasoning": {
            "helpfulness": "", "accuracy": "", "hallucination": "", "safety": "", "summary": ""
        },
        "judge_model": "mock",
        "is_adversarial": False,
        "adversarial_category": None,
        "adversarial_triggered": False,
        "failure_mode_detected": "none",
        "usage": {},
        "anomaly_flagged": False,
        "anomaly_reason": "",
    }


@pytest.fixture
def tmp_db(tmp_path):
    """Provide a temporary database path for each test."""
    return str(tmp_path / "test.db")


@pytest.mark.asyncio
async def test_init_db_creates_tables(tmp_db):
    await init_db(tmp_db)
    import aiosqlite
    async with aiosqlite.connect(tmp_db) as db:
        async with db.execute("SELECT name FROM sqlite_master WHERE type='table'") as cur:
            tables = {row[0] for row in await cur.fetchall()}
    assert "eval_results" in tables
    assert "eval_runs" in tables


@pytest.mark.asyncio
async def test_save_result_persists_to_db(tmp_db):
    await init_db(tmp_db)
    detector = AnomalyDetector(db_path=tmp_db)
    result = make_result(8.5)
    await detector.save_result(result)

    import aiosqlite
    async with aiosqlite.connect(tmp_db) as db:
        async with db.execute("SELECT COUNT(*) FROM eval_results") as cur:
            count = (await cur.fetchone())[0]
    assert count == 1


@pytest.mark.asyncio
async def test_anomaly_not_flagged_with_insufficient_history(tmp_db):
    await init_db(tmp_db)
    detector = AnomalyDetector(db_path=tmp_db)
    result = make_result(9.0)
    checked = await detector.check(result)
    assert checked["anomaly_flagged"] is False


@pytest.mark.asyncio
async def test_anomaly_not_flagged_for_normal_score(tmp_db):
    await init_db(tmp_db)
    detector = AnomalyDetector(db_path=tmp_db)

    # Seed 5 normal scores
    for i, score in enumerate([9.0, 8.5, 9.0, 8.8, 9.2]):
        r = make_result(score)
        r["eval_id"] = f"seed_{i}"
        await detector.save_result(r)

    result = make_result(8.7)
    result["eval_id"] = "normal_test"
    checked = await detector.check(result)
    assert checked["anomaly_flagged"] is False


@pytest.mark.asyncio
async def test_anomaly_flagged_for_score_far_below_mean(tmp_db):
    await init_db(tmp_db)
    detector = AnomalyDetector(db_path=tmp_db)

    # Seed consistent high scores
    for i in range(10):
        r = make_result(9.0)
        r["eval_id"] = f"seed_{i}"
        await detector.save_result(r)

    # Score artificially 2+ std devs below mean
    result = make_result(2.0)
    result["eval_id"] = "anomaly_test"
    checked = await detector.check(result)
    assert checked["anomaly_flagged"] is True
    assert "below" in checked["anomaly_reason"]


@pytest.mark.asyncio
async def test_rolling_stats_returns_correct_mean(tmp_db):
    await init_db(tmp_db)
    detector = AnomalyDetector(db_path=tmp_db)

    for i, score in enumerate([8.0, 9.0, 10.0]):
        r = make_result(score)
        r["eval_id"] = f"s_{i}"
        await detector.save_result(r)

    stats = await detector.get_rolling_stats("headphones")
    assert stats["count"] == 3
    assert stats["mean_overall"] == pytest.approx(9.0)


@pytest.mark.asyncio
async def test_rolling_stats_empty_category_returns_zero(tmp_db):
    await init_db(tmp_db)
    detector = AnomalyDetector(db_path=tmp_db)
    stats = await detector.get_rolling_stats("nonexistent_category")
    assert stats["count"] == 0
    assert stats["mean_overall"] == 0.0


@pytest.mark.asyncio
async def test_pipeline_result_includes_anomaly_fields(tmp_db):
    await init_db(tmp_db)
    pipeline = EvalPipeline(use_mock=True, db_path=tmp_db)
    result = await pipeline.run_single(SAMPLE_QUESTION)
    assert "anomaly_flagged" in result
    assert "anomaly_reason" in result


@pytest.mark.asyncio
async def test_pipeline_saves_result_to_db(tmp_db):
    await init_db(tmp_db)
    pipeline = EvalPipeline(use_mock=True, db_path=tmp_db)
    await pipeline.run_single(SAMPLE_QUESTION)

    import aiosqlite
    async with aiosqlite.connect(tmp_db) as db:
        async with db.execute("SELECT COUNT(*) FROM eval_results") as cur:
            count = (await cur.fetchone())[0]
    assert count == 1
