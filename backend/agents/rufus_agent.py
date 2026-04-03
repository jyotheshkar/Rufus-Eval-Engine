# Rufus shopping assistant agent — generates answers using Claude Haiku + retrieved products

import json
import logging
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

MOCK_PATH = Path(__file__).parent.parent / "data" / "mocks" / "mock_rufus.json"

SYSTEM_PROMPT = """You are Rufus, Amazon's AI shopping assistant. Your job is to help customers find the best products for their needs.

You have been given a customer question and a list of relevant products from the Amazon catalogue. Use ONLY the product information provided — never invent specs, prices, or features that are not in the product list.

Guidelines:
- Be helpful and conversational, not robotic
- Make a clear recommendation when possible
- Mention specific product names, prices, and key specs
- If no products match the query well, say so honestly
- Never make up product information
- Keep responses under 200 words"""


class RufusAgent:
    """Shopping assistant that generates grounded product answers using Claude Haiku."""

    def __init__(self, use_mock: bool | None = None) -> None:
        if use_mock is None:
            use_mock = os.getenv("USE_MOCK", "true").lower() == "true"
        self.use_mock = use_mock
        self.client = anthropic.Anthropic() if not use_mock else None
        logger.info("RufusAgent initialised — use_mock=%s", self.use_mock)

    async def generate_answer(self, query: str, products: list[dict]) -> dict:
        """Generate a shopping answer for the query given retrieved products.

        Returns a dict with keys: answer, model, query, products_used, usage.
        """
        if self.use_mock:
            return self._mock_response(query, products)

        product_context = self._build_product_context(products)
        user_prompt = self._build_user_prompt(query, product_context)

        try:
            response = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=400,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            answer = response.content[0].text
            return {
                "answer": answer,
                "model": response.model,
                "query": query,
                "products_used": [p["id"] for p in products],
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            }
        except Exception as e:
            logger.error("Rufus API call failed: %s", e)
            raise

    def _build_product_context(self, products: list[dict]) -> str:
        """Format retrieved products into a clean context string for the prompt."""
        if not products:
            return "No relevant products found in the catalogue."

        lines = ["AVAILABLE PRODUCTS:\n"]
        for i, p in enumerate(products, 1):
            specs = p.get("specs", {})
            spec_lines = []
            for k, v in specs.items():
                if v is None:
                    continue
                if isinstance(v, list):
                    spec_lines.append(f"{k}: {', '.join(str(x) for x in v)}")
                else:
                    spec_lines.append(f"{k}: {v}")
            specs_str = " | ".join(spec_lines) if spec_lines else "N/A"

            lines.append(
                f"{i}. {p['name']}\n"
                f"   Price: £{p.get('price', 'N/A')} | Rating: {p.get('rating', 'N/A')}/5 | Brand: {p.get('brand', 'N/A')}\n"
                f"   {specs_str}\n"
                f"   Description: {p.get('description', '')}\n"
            )
        return "\n".join(lines)

    def _build_user_prompt(self, query: str, product_context: str) -> str:
        """Combine the customer query and product context into the user message."""
        return f"Customer question: {query}\n\n{product_context}"

    def _mock_response(self, query: str, products: list[dict]) -> dict:
        """Return a static mock response for development — no API call made."""
        with open(MOCK_PATH) as f:
            mock = json.load(f)
        return {
            "answer": mock["mock_response"],
            "model": "mock",
            "query": query,
            "products_used": [p["id"] for p in products],
            "usage": mock["usage"],
        }
