# Tests for the Rufus shopping assistant agent (Phase 3)

import pytest
from backend.agents.rufus_agent import RufusAgent

SAMPLE_PRODUCTS = [
    {
        "id": "prod_001",
        "name": "Sony WH-1000XM5",
        "category": "headphones",
        "price": 279.99,
        "rating": 4.7,
        "brand": "Sony",
        "description": "Industry-leading noise cancelling headphones.",
        "specs": {"battery_life": "30 hours", "connectivity": "Bluetooth 5.2"},
        "tags": ["noise-cancelling", "wireless"],
    },
    {
        "id": "prod_002",
        "name": "JBL Tune 510BT",
        "category": "headphones",
        "price": 39.99,
        "rating": 4.2,
        "brand": "JBL",
        "description": "Affordable wireless headphones with punchy bass.",
        "specs": {"battery_life": "40 hours", "connectivity": "Bluetooth 5.0"},
        "tags": ["wireless", "budget"],
    },
]


@pytest.mark.asyncio
async def test_generate_answer_returns_non_empty_string():
    agent = RufusAgent(use_mock=True)
    result = await agent.generate_answer("best headphones under £100", SAMPLE_PRODUCTS)
    assert isinstance(result["answer"], str)
    assert len(result["answer"]) > 0


@pytest.mark.asyncio
async def test_generate_answer_result_has_all_required_keys():
    agent = RufusAgent(use_mock=True)
    result = await agent.generate_answer("best headphones", SAMPLE_PRODUCTS)
    assert set(result.keys()) == {"answer", "model", "query", "products_used", "usage"}


@pytest.mark.asyncio
async def test_generate_answer_model_is_mock_when_use_mock_true():
    agent = RufusAgent(use_mock=True)
    result = await agent.generate_answer("best headphones", SAMPLE_PRODUCTS)
    assert result["model"] == "mock"


@pytest.mark.asyncio
async def test_generate_answer_products_used_matches_input():
    agent = RufusAgent(use_mock=True)
    result = await agent.generate_answer("best headphones", SAMPLE_PRODUCTS)
    assert result["products_used"] == ["prod_001", "prod_002"]


@pytest.mark.asyncio
async def test_generate_answer_empty_products_does_not_crash():
    agent = RufusAgent(use_mock=True)
    result = await agent.generate_answer("best headphones", [])
    assert isinstance(result["answer"], str)
    assert result["products_used"] == []


@pytest.mark.asyncio
async def test_generate_answer_query_echoed_in_result():
    agent = RufusAgent(use_mock=True)
    query = "lightweight laptop for students"
    result = await agent.generate_answer(query, SAMPLE_PRODUCTS)
    assert result["query"] == query


def test_build_product_context_includes_product_name_and_price():
    agent = RufusAgent(use_mock=True)
    context = agent._build_product_context(SAMPLE_PRODUCTS)
    assert "Sony WH-1000XM5" in context
    assert "279.99" in context


def test_build_product_context_empty_returns_fallback():
    agent = RufusAgent(use_mock=True)
    context = agent._build_product_context([])
    assert "No relevant products" in context
