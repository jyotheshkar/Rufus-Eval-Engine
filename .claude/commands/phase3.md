# Phase 3 — Rufus Agent (Shopping Assistant)

## Goal
Build the shopping assistant agent. It takes a query + retrieved products
and generates a helpful, natural shopping response — exactly like Rufus would.
ALWAYS use mock responses during development unless USE_MOCK=false in .env.

---

## BUDGET RULE — read this first
During ALL development and testing in this phase:
- Load USE_MOCK from .env
- If USE_MOCK=true → return mock response from backend/data/mocks/mock_rufus.json
- If USE_MOCK=false → call real Anthropic API
- NEVER set USE_MOCK=false during development loops
- Only set USE_MOCK=false when doing a final real test run

---

## Step 1 — Create mock response file

File: backend/data/mocks/mock_rufus.json

```json
{
  "mock_response": "Based on your requirements, I'd recommend the Sony WH-1000XM5 headphones. They offer industry-leading noise cancellation, 30 hours of battery life, and excellent sound quality. At £279.99, they're a premium option, but worth it for daily commuters or remote workers. The Jabra Evolve2 at £89.99 is a great mid-range alternative if budget is a concern.",
  "model": "mock",
  "usage": {"input_tokens": 0, "output_tokens": 0}
}
```

---

## Step 2 — Build rufus_agent.py

File: backend/agents/rufus_agent.py

### System prompt for Rufus:
```
You are Rufus, Amazon's AI shopping assistant. Your job is to help customers
find the best products for their needs.

You have been given a customer question and a list of relevant products from
the Amazon catalogue. Use ONLY the product information provided — never
invent specs, prices, or features that are not in the product list.

Guidelines:
- Be helpful and conversational, not robotic
- Make a clear recommendation when possible
- Mention specific product names, prices, and key specs
- If no products match the query well, say so honestly
- Never make up product information
- Keep responses under 200 words
```

### Class interface:
```python
class RufusAgent:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock
        self.client = anthropic.Anthropic() if not use_mock else None

    async def generate_answer(
        self,
        query: str,
        products: list[dict]
    ) -> dict:
        # Returns:
        # {
        #   "answer": str,
        #   "model": str,
        #   "query": str,
        #   "products_used": list[str],  # product ids
        #   "usage": dict
        # }
        pass

    def _build_product_context(self, products: list[dict]) -> str:
        # Format products into clean context string for the prompt
        pass

    def _build_user_prompt(self, query: str, product_context: str) -> str:
        # Combine query + product context into user message
        pass
```

### Product context format in prompt:
```
AVAILABLE PRODUCTS:

1. Sony WH-1000XM5 Wireless Headphones
   Price: £279.99 | Rating: 4.7/5 | Brand: Sony
   Battery: 30 hours | Bluetooth 5.2 | Weight: 250g
   Waterproof: No
   Description: Industry-leading noise cancelling headphones...

2. JBL Tune 510BT...
```

---

## Step 3 — Build a test script

File: backend/scripts/test_rufus_agent.py

Test with USE_MOCK=true first, then optionally with USE_MOCK=false.

```python
test_cases = [
    "What are the best wireless headphones under £100?",
    "I need a laptop for university — lightweight and long battery",
    "Compare these two smartwatches for fitness tracking"
]
```

Print the full response for each. Check:
- Response is under 200 words
- Response mentions specific product names
- Response doesn't mention any specs not in the provided products

---

## Step 4 — Verify phase 3

```bash
# Test with mock (free)
USE_MOCK=true python backend/scripts/test_rufus_agent.py

# Only run this once to verify real API works
USE_MOCK=false python backend/scripts/test_rufus_agent.py
```

## Phase 3 complete when:
- rufus_agent.py fully implemented
- Mock mode works with zero API calls
- Real mode tested once with a single query
- Responses are natural, under 200 words, grounded in product data
