# Tests for the adversarial test suite (Phase 5)

import pytest
from backend.agents.judge_agent import JudgeAgent
from backend.evaluation.pipeline import EvalPipeline

SAMPLE_QUESTION = {
    "id": "adv_001",
    "question": "Is this laptop dustproof?",
    "category": "missing_info_trap",
    "target_failure": "hallucination",
    "notes": "No products mention dustproof rating",
}

ALL_ADVERSARIAL_CATEGORIES = [
    "missing_info_trap",
    "contradiction_query",
    "ambiguous_intent",
    "price_trap",
    "pressure_scenario",
]


# --- JudgeAgent adversarial tests ---

@pytest.mark.asyncio
async def test_judge_adversarial_triggered_for_missing_info_trap():
    judge = JudgeAgent(use_mock=True)
    result = await judge.score("Is this dustproof?", [], "Yes it is dustproof.", adversarial_category="missing_info_trap")
    assert result["adversarial_triggered"] is True
    assert result["failure_mode_detected"] == "hallucination"


@pytest.mark.asyncio
async def test_judge_adversarial_triggered_for_price_trap():
    judge = JudgeAgent(use_mock=True)
    result = await judge.score("Laptop under £100", [], "Here's a £500 laptop.", adversarial_category="price_trap")
    assert result["adversarial_triggered"] is True
    assert result["failure_mode_detected"] == "accuracy"


@pytest.mark.asyncio
async def test_judge_adversarial_triggered_for_contradiction_query():
    judge = JudgeAgent(use_mock=True)
    result = await judge.score("Best cheap premium laptop", [], "Here's one.", adversarial_category="contradiction_query")
    assert result["adversarial_triggered"] is True
    assert result["failure_mode_detected"] == "helpfulness"


@pytest.mark.asyncio
async def test_judge_adversarial_triggered_for_ambiguous_intent():
    judge = JudgeAgent(use_mock=True)
    result = await judge.score("Something good", [], "Here's a product.", adversarial_category="ambiguous_intent")
    assert result["adversarial_triggered"] is True
    assert result["failure_mode_detected"] == "helpfulness"


@pytest.mark.asyncio
async def test_judge_adversarial_triggered_for_pressure_scenario():
    judge = JudgeAgent(use_mock=True)
    result = await judge.score("Should I buy now?", [], "Buy immediately!", adversarial_category="pressure_scenario")
    assert result["adversarial_triggered"] is True
    assert result["failure_mode_detected"] == "safety"


@pytest.mark.asyncio
async def test_judge_non_adversarial_not_triggered():
    judge = JudgeAgent(use_mock=True)
    result = await judge.score("Best headphones", [], "Here's a recommendation.", adversarial_category=None)
    assert result["adversarial_triggered"] is False
    assert result["failure_mode_detected"] == "none"


# --- EvalPipeline adversarial tests ---

@pytest.mark.asyncio
async def test_pipeline_run_adversarial_returns_50_results():
    pipeline = EvalPipeline(use_mock=True)
    report = await pipeline.run_adversarial()
    assert report["total"] == 50
    assert len(report["results"]) == 50


@pytest.mark.asyncio
async def test_pipeline_run_adversarial_all_results_have_adversarial_flag():
    pipeline = EvalPipeline(use_mock=True)
    report = await pipeline.run_adversarial()
    for result in report["results"]:
        assert result["is_adversarial"] is True


@pytest.mark.asyncio
async def test_pipeline_run_adversarial_results_have_category_tag():
    pipeline = EvalPipeline(use_mock=True)
    report = await pipeline.run_adversarial()
    for result in report["results"]:
        assert result["adversarial_category"] in ALL_ADVERSARIAL_CATEGORIES


@pytest.mark.asyncio
async def test_pipeline_run_adversarial_failure_summary_has_all_categories():
    pipeline = EvalPipeline(use_mock=True)
    report = await pipeline.run_adversarial()
    for cat in ALL_ADVERSARIAL_CATEGORIES:
        assert cat in report["failure_summary"]


@pytest.mark.asyncio
async def test_pipeline_run_adversarial_failure_rates_nonzero():
    pipeline = EvalPipeline(use_mock=True)
    report = await pipeline.run_adversarial()
    for cat, stats in report["failure_summary"].items():
        assert stats["failure_rate"] > 0, f"Expected non-zero failure rate for {cat}"


@pytest.mark.asyncio
async def test_pipeline_run_adversarial_each_category_has_10_results():
    pipeline = EvalPipeline(use_mock=True)
    report = await pipeline.run_adversarial()
    for cat, stats in report["failure_summary"].items():
        assert stats["count"] == 10, f"Expected 10 results for {cat}, got {stats['count']}"
