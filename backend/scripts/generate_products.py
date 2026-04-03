# Generates 1000 synthetic Amazon-style products using Claude Haiku and saves to data/products.json

import json
import os
import sys
import anthropic
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OUTPUT_PATH = Path(__file__).parent.parent / "data" / "products.json"

CATEGORIES = {
    "headphones": 100,
    "laptops": 100,
    "smartphones": 100,
    "tablets": 80,
    "smartwatches": 80,
    "cameras": 80,
    "speakers": 80,
    "gaming": 80,
    "monitors": 80,
    "accessories": 120,
}

BATCH_SIZE = 20

PROMPT_TEMPLATE = """Generate {count} synthetic Amazon-style products in the category: {category}.

Return ONLY a valid JSON array. Each object must have exactly these fields:
{{
  "id": "prod_XXX",
  "name": "string",
  "category": "{category}",
  "price": float (GBP, realistic for category),
  "currency": "GBP",
  "rating": float (3.0-5.0),
  "review_count": int (10-50000),
  "brand": "string",
  "description": "string (2-3 sentences)",
  "specs": {{
    "battery_life": "string or null",
    "connectivity": "string or null",
    "weight": "string",
    "waterproof": bool,
    "color": ["string"]
  }},
  "tags": ["string"],
  "in_stock": bool,
  "embedding": []
}}

Use realistic brand names, prices, and specs for the {category} category.
Start IDs from prod_{start_id:03d}.
Return only the JSON array, no explanation."""


def generate_batch(client: anthropic.Anthropic, category: str, count: int, start_id: int) -> list:
    """Generate a batch of products for a given category."""
    prompt = PROMPT_TEMPLATE.format(
        count=count,
        category=category,
        start_id=start_id,
    )
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def main() -> None:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_key_here":
        print("ERROR: Set ANTHROPIC_API_KEY in backend/.env before running this script.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Load existing progress if any
    all_products: list = []
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH) as f:
            all_products = json.load(f)
        print(f"Resuming — {len(all_products)} products already generated.")

    generated_categories = {p["category"] for p in all_products}
    global_id = len(all_products) + 1

    for category, total_count in CATEGORIES.items():
        if category in generated_categories:
            print(f"Skipping {category} — already done.")
            continue

        print(f"\nGenerating {total_count} {category} products...")
        category_products: list = []
        remaining = total_count

        while remaining > 0:
            batch_count = min(BATCH_SIZE, remaining)
            print(f"  Batch: {batch_count} products (id starts at {global_id})")
            try:
                batch = generate_batch(client, category, batch_count, global_id)
                # Re-assign IDs sequentially to avoid collisions
                for i, product in enumerate(batch):
                    product["id"] = f"prod_{global_id + i:04d}"
                category_products.extend(batch)
                global_id += batch_count
                remaining -= batch_count
            except Exception as e:
                print(f"  ERROR in batch: {e}")
                break

        all_products.extend(category_products)
        # Save after every category to preserve progress
        with open(OUTPUT_PATH, "w") as f:
            json.dump(all_products, f, indent=2)
        print(f"  Saved. Total so far: {len(all_products)}")

    # Final summary
    print(f"\n--- Generation complete ---")
    print(f"Total products: {len(all_products)}")
    from collections import Counter
    counts = Counter(p["category"] for p in all_products)
    for cat, count in sorted(counts.items()):
        prices = [p["price"] for p in all_products if p["category"] == cat]
        print(f"  {cat}: {count} products | £{min(prices):.2f}–£{max(prices):.2f}")


if __name__ == "__main__":
    main()
