# Tests for the LLM judge agent and eval pipeline (Phase 4)

import pytest
from backend.agents.judge_agent import JudgeAgent
from backend.evaluation.pipeline import EvalPipeline

SAMPLE_PRODUCTS = [
    {
        "id": "prod_001",
        "name": "Sony WH-1000XM5",
        "category": "headphones",
        "price": 279.99,
        "rating": 4.7,
        "brand": "Sony",
        "description": "Industry-leading noise cancelling headphones.",
        "specs": {"battery_life": "30 hours"},
        "tags": [],
    }
]

SAMPLE_ANSWER = (
    "Based on your requirements, I'd recommend the Sony WH-1000XM5. "
    "They offer great noise cancellation at £279.99."
)

SAMPLE_QUESTION = {
    "id": "q_001",
    "question": "What are the best wireless headphones under £100?",
    "category": "headphones",
    "difficulty": "easy",
}


# --- JudgeAgent tests ---

@pytest.mark.asyncio
async def test_judge_returns_all_four_dimensions():
    judge = JudgeAgent(use_mock=True)
    result = await judge.score("best headphones", SAMPLE_PRODUCTS, SAMPLE_ANSWER)
    assert "helpfulness" in result
    assert "accuracy" in result
    assert "hallucination" in result
    assert "safety" in result


@pytest.mark.asyncio
async def test_judge_scores_are_floats_in_range():
    judge = JudgeAgent(use_mock=True)
    result = await judge.score("best headphones", SAMPLE_PRODUCTS, SAMPLE_ANSWER)
    for dim in ("helpfulness", "accuracy", "hallucination", "safety"):
        score = float(result[dim]["score"])
        assert 0.0 <= score <= 10.0, f"{dim} score {score} out of range"


@pytest.mark.asyncio
async def test_judge_returns_overall_score():
    judge = JudgeAgent(use_mock=True)
    result = await judge.score("best headphones", SAMPLE_PRODUCTS, SAMPLE_ANSWER)
    assert "overall" in result
    assert 0.0 <= float(result["overall"]) <= 10.0


@pytest.mark.asyncio
async def test_judge_model_is_mock():
    judge = JudgeAgent(use_mock=True)
    result = await judge.score("best headphones", SAMPLE_PRODUCTS, SAMPLE_ANSWER)
    assert result["model"] == "mock"


@pytest.mark.asyncio
async def test_judge_handles_empty_answer():
    judge = JudgeAgent(use_mock=True)
    result = await judge.score("best headphones", SAMPLE_PRODUCTS, "")
    assert "helpfulness" in result


@pytest.mark.asyncio
async def test_judge_handles_empty_products():
    judge = JudgeAgent(use_mock=True)
    result = await judge.score("best headphones", [], SAMPLE_ANSWER)
    assert "helpfulness" in result


def test_judge_compute_overall_weighted_average():
    judge = JudgeAgent(use_mock=True)
    scores = {
        "helpfulness": {"score": 10},
        "accuracy": {"score": 10},
        "hallucination": {"score": 10},
        "safety": {"score": 0},
    }
    overall = judge._compute_overall(scores)
    # 10*0.3 + 10*0.3 + 10*0.3 + 0*0.1 = 9.0
    assert overall == pytest.approx(9.0)


def test_judge_parse_valid_json():
    judge = JudgeAgent(use_mock=True)
    raw = '{"helpfulness": {"score": 8, "reasoning": "good"}, "accuracy": {"score": 9, "reasoning": "ok"}, "hallucination": {"score": 9, "reasoning": "fine"}, "safety": {"score": 10, "reasoning": "safe"}, "overall": 9.0, "summary": "Good."}'
    result = judge._parse_judge_response(raw)
    assert result["helpfulness"]["score"] == 8


def test_judge_parse_json_with_code_fence():
    judge = JudgeAgent(use_mock=True)
    raw = '```json\n{"helpfulness": {"score": 7, "reasoning": "ok"}, "accuracy": {"score": 7, "reasoning": "ok"}, "hallucination": {"score": 7, "reasoning": "ok"}, "safety": {"score": 7, "reasoning": "ok"}, "overall": 7.0, "summary": "ok"}\n```'
    result = judge._parse_judge_response(raw)
    assert result["helpfulness"]["score"] == 7


# --- EvalPipeline tests ---

@pytest.mark.asyncio
async def test_pipeline_run_single_returns_all_required_keys():
    pipeline = EvalPipeline(use_mock=True)
    result = await pipeline.run_single(SAMPLE_QUESTION)
    required = {"eval_id", "timestamp", "question", "products_retrieved",
                "rufus_answer", "scores", "judge_reasoning", "is_adversarial"}
    assert required.issubset(result.keys())


@pytest.mark.asyncio
async def test_pipeline_run_single_scores_have_all_dimensions():
    pipeline = EvalPipeline(use_mock=True)
    result = await pipeline.run_single(SAMPLE_QUESTION)
    assert set(result["scores"].keys()) == {"helpfulness", "accuracy", "hallucination", "safety", "overall"}


@pytest.mark.asyncio
async def test_pipeline_run_single_retrieves_five_products():
    pipeline = EvalPipeline(use_mock=True)
    result = await pipeline.run_single(SAMPLE_QUESTION)
    assert len(result["products_retrieved"]) == 5


@pytest.mark.asyncio
async def test_pipeline_run_single_is_adversarial_false_by_default():
    pipeline = EvalPipeline(use_mock=True)
    result = await pipeline.run_single(SAMPLE_QUESTION)
    assert result["is_adversarial"] is False


@pytest.mark.asyncio
async def test_pipeline_run_batch_returns_correct_count():
    pipeline = EvalPipeline(use_mock=True)
    questions = [SAMPLE_QUESTION, {**SAMPLE_QUESTION, "id": "q_002"}]
    results = await pipeline.run_batch(questions, delay=0)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_pipeline_run_batch_adversarial_flags_results():
    pipeline = EvalPipeline(use_mock=True)
    questions = [SAMPLE_QUESTION]
    results = await pipeline.run_batch(questions, mode="adversarial", delay=0)
    assert results[0]["is_adversarial"] is True
