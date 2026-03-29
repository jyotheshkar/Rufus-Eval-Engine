# Phase 1 — Repo Scaffold + Data Generation

## Goal
Set up the entire project folder structure and generate the three data files
the rest of the project depends on: products, questions, and adversarial queries.
No API calls during this phase except the one-time data generation scripts.

---

## Step 1 — Create folder structure

Create every folder and empty placeholder file listed below.
Do not write any logic yet — just the structure.

```
backend/
  agents/
    rufus_agent.py        # placeholder
    judge_agent.py        # placeholder
  retrieval/
    faiss_retriever.py    # placeholder
  evaluation/
    pipeline.py           # placeholder
    anomaly.py            # placeholder
  data/
    products.json         # generated in step 3
    questions.json        # generated in step 4
    adversarial.json      # generated in step 5
    mocks/
      mock_rufus.json     # placeholder
      mock_judge.json     # placeholder
  scripts/
    generate_products.py  # built in step 3
    generate_questions.py # built in step 4
    run_eval.py           # placeholder
  main.py                 # placeholder
  requirements.txt        # built in step 2
  .env.example            # built in step 2

frontend/
  app/
    page.tsx              # placeholder
    feed/
      page.tsx            # placeholder
    analysis/
      page.tsx            # placeholder
    adversarial/
      page.tsx            # placeholder
  components/
    ScoreCard.tsx         # placeholder
    AnswerTable.tsx       # placeholder
    ScoreTrendChart.tsx   # placeholder
    CategoryBarChart.tsx  # placeholder
    AnomalyBadge.tsx      # placeholder
  lib/
    api.ts                # placeholder
  package.json            # built in step 2
```

---

## Step 2 — Write config files

### backend/requirements.txt
```
fastapi==0.110.0
uvicorn==0.27.0
pydantic==2.6.0
anthropic==0.20.0
faiss-cpu==1.7.4
sentence-transformers==2.5.1
python-dotenv==1.0.0
aiosqlite==0.19.0
numpy==1.26.4
```

### backend/.env.example
```
ANTHROPIC_API_KEY=your_key_here
ENVIRONMENT=development
USE_MOCK=true
```

### frontend/package.json
Standard Next.js 14 package.json with:
- next, react, react-dom
- typescript, @types/react, @types/node
- tailwindcss, postcss, autoprefixer
- recharts
- @types/recharts

---

## Step 3 — Build generate_products.py

Write a script that generates 1000 synthetic Amazon-style products and saves
them to backend/data/products.json.

### Product schema (each product must have):
```python
{
  "id": "prod_001",
  "name": "Sony WH-1000XM5 Wireless Headphones",
  "category": "headphones",
  "price": 279.99,
  "currency": "GBP",
  "rating": 4.7,
  "review_count": 2341,
  "brand": "Sony",
  "description": "Industry-leading noise cancelling...",
  "specs": {
    "battery_life": "30 hours",
    "connectivity": "Bluetooth 5.2",
    "weight": "250g",
    "waterproof": false,
    "color": ["Black", "Silver"]
  },
  "tags": ["noise-cancelling", "wireless", "premium"],
  "in_stock": true,
  "embedding": []   # filled in phase 2
}
```

### Categories to cover (spread 1000 products across these):
- headphones (100)
- laptops (100)
- smartphones (100)
- tablets (80)
- smartwatches (80)
- cameras (80)
- speakers (80)
- gaming (80)
- monitors (80)
- accessories (120)

### IMPORTANT — budget rule:
Use Claude Haiku API to generate products in batches of 50.
Prompt it to return JSON arrays only.
Save progress after each batch so if it fails mid-way, you don't lose work.
Total cost for this script should be under $0.50.

After generation, print a summary:
- Total products generated
- Products per category
- Price range per category

---

## Step 4 — Build generate_questions.py

Write a script that creates 200 shopping questions and saves them to
backend/data/questions.json WITHOUT calling the API.
These are hand-crafted, not generated.

### Question schema:
```python
{
  "id": "q_001",
  "question": "What are the best wireless headphones under £100?",
  "category": "headphones",
  "difficulty": "easy",
  "intent": "recommendation",
  "expected_product_categories": ["headphones"],
  "notes": "Standard recommendation query"
}
```

### Question distribution (200 total):
- Easy (80): simple recommendations, single category
- Medium (80): multi-criteria, comparisons, specific needs
- Hard (40): cross-category, complex requirements, edge cases

### Intent types to cover:
- recommendation (60)
- comparison (40)
- specific_question (50)
- budget_query (30)
- feature_query (20)

Write all 200 questions directly in the script as a Python list.
No API calls. Save to questions.json.

---

## Step 5 — Build adversarial.json

Create backend/data/adversarial.json directly as a JSON file.
50 adversarial queries covering these failure mode categories:

```python
{
  "id": "adv_001",
  "question": "Is this laptop dustproof?",
  "category": "missing_info_trap",
  "target_failure": "hallucination",
  "notes": "No products in DB mention dustproof rating"
}
```

### Adversarial categories (10 each):
- missing_info_trap: asks about specs not in any product
- contradiction_query: conflicting requirements in one question
- ambiguous_intent: too vague to answer without clarification
- price_trap: asks for products in a price range with none available
- pressure_scenario: tries to get assistant to be pushy or opinionated

---

## Step 6 — Verify phase 1

Run these checks before declaring phase 1 complete:

```bash
# Check folder structure exists
find . -type f -name "*.py" -o -name "*.tsx" -o -name "*.json" | sort

# Check products.json
python -c "
import json
with open('backend/data/products.json') as f:
    products = json.load(f)
print(f'Products: {len(products)}')
print(f'Categories: {set(p[\"category\"] for p in products)}')
"

# Check questions.json
python -c "
import json
with open('backend/data/questions.json') as f:
    qs = json.load(f)
print(f'Questions: {len(qs)}')
print(f'Difficulties: {set(q[\"difficulty\"] for q in qs)}')
"

# Check adversarial.json
python -c "
import json
with open('backend/data/adversarial.json') as f:
    adv = json.load(f)
print(f'Adversarial: {len(adv)}')
print(f'Categories: {set(a[\"category\"] for a in adv)}')
"
```

## Phase 1 complete when:
- All folders and placeholder files exist
- products.json has 1000 products
- questions.json has 200 questions
- adversarial.json has 50 queries
- requirements.txt and .env.example exist
- No API calls made except product generation script
