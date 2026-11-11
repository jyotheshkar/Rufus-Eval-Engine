"""A blocked SDK must not prevent the event loop from serving other work."""
import asyncio
import json
import os
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from backend.agents.rufus_agent import RufusAgent
from backend.agents.judge_agent import JudgeAgent

class NonBlockingAgentTests(unittest.IsolatedAsyncioTestCase):
    async def _check(self, agent, call):
        started, release = threading.Event(), threading.Event()
        def create(**kwargs):
            started.set()
            if not release.wait(2):
                raise TimeoutError('event loop failed to release SDK worker')
            scores = {d: {'score': 8, 'reasoning': 'fixture'} for d in
                      ('helpfulness', 'accuracy', 'hallucination', 'safety')}
            return SimpleNamespace(content=[SimpleNamespace(text=json.dumps(scores))],
                model='test', usage=SimpleNamespace(input_tokens=1, output_tokens=1))
        agent.use_mock = False
        agent.client = SimpleNamespace(messages=SimpleNamespace(create=create))
        task = asyncio.create_task(call())
        try:
            for _ in range(100):
                if started.is_set():
                    break
                await asyncio.sleep(.005)
            self.assertTrue(started.is_set())
            self.assertFalse(task.done())
        finally:
            release.set()
        result = await task
        self.assertEqual(result['model'], 'test')

    async def test_answer_sdk_does_not_block_loop(self):
        a = RufusAgent(use_mock=True)
        await self._check(a, lambda: a.generate_answer('question', []))

    async def test_judge_sdk_does_not_block_loop(self):
        a = JudgeAgent(use_mock=True)
        await self._check(a, lambda: a.score('question', [], 'answer'))


class LiveClientConstructionTests(unittest.TestCase):
    def test_supported_sdk_transport_constructs_without_network(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-not-a-real-key'}, clear=True):
            for agent_type in (RufusAgent, JudgeAgent):
                agent = agent_type(use_mock=False)
                try:
                    self.assertIsNotNone(agent.client)
                    self.assertEqual(agent.client.max_retries, 2)
                finally:
                    agent.client.close()
