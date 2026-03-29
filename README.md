# Rufus Eval Engine

A production-style LLM evaluation framework for an AI shopping assistant (Rufus), built by Jyothesh Karnam as a portfolio project targeting Language Engineer and Applied ML roles at Amazon.

## What it does

Rufus answers millions of shopping questions. This system automatically judges whether those answers are any good. It runs each answer through a second LLM-as-a-judge pipeline that scores across four dimensions — helpfulness, accuracy, hallucination, and safety — surfaces quality trends in a dashboard, and runs adversarial tests to expose failure modes.

## How it works

1. A question is pulled from the question bank or adversarial test suite
2. FAISS retrieves the top-5 matching products from the product catalog
3. The Rufus agent (Claude Haiku) generates a shopping answer
4. The LLM judge (Claude Haiku) scores the answer on 4 dimensions (0–10 each)
5. An anomaly detector flags drops vs the rolling average
6. Results are saved to SQLite and surfaced in the frontend dashboard

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Recharts |
| Backend | Python 3.11, FastAPI, Pydantic |
| Vector Search | FAISS |
| LLM | Claude Haiku (Anthropic API) |
| Storage | SQLite + JSON |
| Deployment | Vercel (frontend), Railway (backend) |

## Project Status

Under active development — 9 phases planned, covering data generation, vector store, agent pipeline, LLM judge, adversarial suite, anomaly detection, API, frontend, and deployment.
