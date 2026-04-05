# Rufus Eval Engine

A production-style LLM evaluation framework for an AI shopping assistant (Rufus), built by Jyothesh Karnam as a portfolio project targeting Language Engineer and Applied ML roles at Amazon.

## What it does

Rufus answers millions of shopping questions. This system automatically judges whether those answers are any good. It runs each answer through a second LLM-as-a-judge pipeline that scores across four dimensions — helpfulness, accuracy, hallucination, and safety — surfaces quality trends in a dashboard, and runs adversarial tests to expose failure modes.

## Live Demo

| Service | URL |
|---------|-----|
| Frontend dashboard | *(deploy to Vercel — add URL here)* |
| Backend API | *(deploy to Railway — add URL here)* |
| API docs | `<railway-url>/docs` |

## How it works

1. A question is pulled from the question bank (200 questions) or adversarial suite (50 queries)
2. FAISS retrieves the top-5 matching products from a 1,000-product catalog
3. The Rufus agent (Claude Haiku) generates a shopping answer using retrieved context
4. The LLM judge (Claude Haiku) scores the answer on 4 dimensions (0–10 each)
5. An anomaly detector flags scores that drop more than 1.5 standard deviations below the category mean
6. Results are saved to SQLite and surfaced in the Next.js dashboard

## Evaluation Dimensions

| Dimension | What it measures | Score |
|-----------|-----------------|-------|
| Helpfulness | Did it answer what the customer actually asked? | 0–10 |
| Accuracy | Are the product facts correct? | 0–10 |
| Hallucination | Did it invent specs or features? (10 = none) | 0–10 |
| Safety | Did it mislead or pressure the customer? | 0–10 |

## Dashboard Screens

- **Overview** — KPI cards, score trend chart, anomaly count, category breakdown
- **Answer Feed** — Browse all eval results, filter by category, see full question + answer + scores
- **Weak Spots** — Worst-performing categories and lowest-scoring answers
- **Adversarial** — Failure mode breakdown across 5 adversarial categories
- **Visualise Dataset** — Browse the raw products, questions, and adversarial queries

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Recharts |
| Backend | Python 3.11, FastAPI, Pydantic |
| Vector Search | FAISS (cosine similarity over sentence-transformers embeddings) |
| LLM | Claude Haiku (Anthropic API) |
| Storage | SQLite + JSON |
| Deployment | Vercel (frontend), Railway (backend) |

## Project Structure

```
rufus-eval-engine/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── agents/
│   │   ├── rufus_agent.py       # Shopping assistant (Claude Haiku)
│   │   └── judge_agent.py       # LLM judge (Claude Haiku, 4 dimensions)
│   ├── retrieval/
│   │   └── faiss_retriever.py   # FAISS vector store + top-5 retrieval
│   ├── evaluation/
│   │   ├── pipeline.py          # End-to-end eval pipeline
│   │   └── anomaly.py           # Anomaly detection (rolling stats)
│   ├── routes/
│   │   ├── evals.py             # /evals endpoints
│   │   ├── stats.py             # /stats endpoints
│   │   ├── adversarial.py       # /adversarial endpoints
│   │   └── data.py              # /data endpoints (dataset browser)
│   ├── data/
│   │   ├── products.json        # 1,000 synthetic products (5 categories)
│   │   ├── questions.json       # 200 shopping questions (3 difficulty levels)
│   │   ├── adversarial.json     # 50 adversarial queries (5 failure modes)
│   │   └── eval_results.db      # SQLite database
│   ├── scripts/
│   │   └── run_eval.py          # Run evaluation pipeline
│   ├── requirements.txt
│   ├── Procfile                 # Railway start command
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Overview screen
│   │   ├── feed/page.tsx        # Answer Feed screen
│   │   ├── analysis/page.tsx    # Weak Spots screen
│   │   ├── adversarial/page.tsx # Adversarial screen
│   │   └── dataset/page.tsx     # Visualise Dataset screen
│   ├── components/
│   │   ├── Nav.tsx              # Shared navigation bar
│   │   ├── ScoreCard.tsx        # KPI metric card
│   │   ├── ScoreTrendChart.tsx  # Line chart (Recharts)
│   │   ├── CategoryBarChart.tsx # Bar chart (Recharts)
│   │   ├── AnswerTable.tsx      # Paginated eval results table
│   │   └── AnomalyBadge.tsx     # Anomaly count badge
│   └── lib/
│       ├── api.ts               # All API calls (centralised)
│       └── types.ts             # TypeScript interfaces
└── docs/                        # Phase documentation (phases 1–9)
```

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- An Anthropic API key (only needed for live eval runs)

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY, keep USE_MOCK=true for dev
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

API docs available at: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
# For local dev, backend defaults to http://localhost:8000
npx next dev -p 3000
```

Open: http://localhost:3000

### Running Evaluations

**With mocks (free, for development):**
```bash
USE_MOCK=true python backend/scripts/run_eval.py --count 10
```

**With live API (costs ~$0.015 per question):**
```bash
USE_MOCK=false python backend/scripts/run_eval.py --count 20
```

## Deployment

### Backend → Railway

1. Create a project at [railway.app](https://railway.app)
2. Connect your GitHub repo → select `rufus-eval-engine`
3. Set root directory: `/backend`
4. Add environment variables:
   - `ANTHROPIC_API_KEY` — your Anthropic key
   - `USE_MOCK` — `false`
   - `ENVIRONMENT` — `production`
5. Railway auto-deploys via `Procfile`

### Frontend → Vercel

1. Connect repo at [vercel.com/new](https://vercel.com/new)
2. Set root directory: `frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` — your Railway backend URL (e.g. `https://rufus-eval-engine.up.railway.app`)
4. Deploy

## Adversarial Test Categories

| Category | What it tests |
|----------|--------------|
| `missing_info_trap` | Questions with deliberately incomplete information |
| `contradiction_query` | Queries with contradictory requirements |
| `ambiguous_intent` | Queries where the user intent is unclear |
| `price_trap` | Queries designed to expose price hallucination |
| `pressure_scenario` | Queries that test for high-pressure sales language |

## Build Status

- Phases 1–8: Complete
- Phase 9: Deployment in progress
