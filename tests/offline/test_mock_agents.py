"""Focused fixture-contract checks: no retrieval, evaluation DB or model calls."""

import os
import unittest
from unittest.mock import patch

from backend.agents.judge_agent import JudgeAgent
from backend.agents.rufus_agent import RufusAgent


PRODUCTS = [
    {"id": "fixture_1", "name": "Example product", "price": 10, "specs": {}}
]


class MockAgentContracts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Fail immediately if a mock path tries to construct an external API client.
        blocker = patch(
            "anthropic.Anthropic",
            side_effect=AssertionError("Mock checks must not construct an API client"),
        )
        blocker.start()
        self.addCleanup(blocker.stop)

    async def test_explicit_mock_overrides_live_environment(self):
        with patch.dict(os.environ, {"USE_MOCK": "false"}):
            assistant = RufusAgent(use_mock=True)
            judge = JudgeAgent(use_mock=True)
            self.assertIsNone(assistant.client)
            self.assertIsNone(judge.client)
            answer = await assistant.generate_answer("fixture question", PRODUCTS)
            score = await judge.score("fixture question", PRODUCTS, answer["answer"])
        self.assertEqual(answer["model"], "mock")
        self.assertEqual(score["model"], "mock")

    async def test_default_mode_is_mock_without_a_key(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(RufusAgent().use_mock)
            self.assertTrue(JudgeAgent().use_mock)

    async def test_mock_answer_preserves_request_metadata(self):
        assistant = RufusAgent(use_mock=True)
        answer = await assistant.generate_answer("fixture question", PRODUCTS)
        repeated = await assistant.generate_answer("fixture question", PRODUCTS)
        self.assertEqual(answer, repeated)
        self.assertEqual(answer["query"], "fixture question")
        self.assertEqual(answer["products_used"], ["fixture_1"])
        self.assertEqual(answer["usage"], {"input_tokens": 0, "output_tokens": 0})
        self.assertIsInstance(answer["answer"], str)
        self.assertTrue(answer["answer"])

    async def test_empty_product_context_is_supported(self):
        answer = await RufusAgent(use_mock=True).generate_answer("fixture", [])
        self.assertEqual(answer["products_used"], [])

    async def test_adversarial_fixtures_map_to_expected_failure_dimensions(self):
        judge = JudgeAgent(use_mock=True)
        expected = {
            "missing_info_trap": "hallucination",
            "price_trap": "accuracy",
            "contradiction_query": "helpfulness",
            "ambiguous_intent": "helpfulness",
            "pressure_scenario": "safety",
        }
        for category, dimension in expected.items():
            with self.subTest(category=category):
                result = await judge.score("fixture", PRODUCTS, "answer", category)
                self.assertEqual(result["model"], "mock")
                self.assertTrue(result["adversarial_triggered"])
                self.assertEqual(result["failure_mode_detected"], dimension)
                self.assertLess(result[dimension]["score"], 7)
                self.assertEqual(result["overall"], judge._compute_overall(result))

    async def test_normal_fixture_is_not_mutated_by_adversarial_call(self):
        judge = JudgeAgent(use_mock=True)
        before = await judge.score("fixture", PRODUCTS, "answer")
        await judge.score("fixture", PRODUCTS, "answer", "price_trap")
        after = await judge.score("fixture", PRODUCTS, "answer")
        self.assertEqual(before, after)
        self.assertFalse(after["adversarial_triggered"])

    async def test_unknown_category_does_not_invent_a_failure(self):
        result = await JudgeAgent(use_mock=True).score(
            "fixture", PRODUCTS, "answer", "unknown_fixture_category"
        )
        self.assertFalse(result["adversarial_triggered"])

    def test_judge_parses_json_code_fence(self):
        result = JudgeAgent(use_mock=True)._parse_judge_response(
            '```json\n{"summary": "fixture"}\n```'
        )
        self.assertEqual(result, {"summary": "fixture"})

    def test_judge_rejects_malformed_json(self):
        with self.assertRaises(ValueError):
            JudgeAgent(use_mock=True)._parse_judge_response("not valid json")

    def test_weighted_overall_score(self):
        scores = {
            "helpfulness": {"score": 10},
            "accuracy": {"score": 10},
            "hallucination": {"score": 10},
            "safety": {"score": 0},
        }
        self.assertEqual(JudgeAgent(use_mock=True)._compute_overall(scores), 9.0)


if __name__ == "__main__":
    unittest.main()
