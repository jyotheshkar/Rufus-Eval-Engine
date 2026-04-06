# Phase 9 — Integration + Deployment
**Status:** Complete
**Date completed:** 2026-04-05
**Built by:** Claude (claude-sonnet-4-6) + Jyothesh Karnam

---

## What this phase built

Phase 9 wires the entire system together and prepares it for production deployment. The backend is configured to run on Railway (a cloud hosting platform) and the frontend on Vercel. The README was rewritten to serve as a complete project reference — setup instructions, architecture overview, deployment guide, and portfolio context for Amazon Language Engineer roles.

---

## Why this phase matters

Phases 1–8 built a working system locally. Phase 9 makes it accessible to anyone on the internet — a recruiter, a hiring manager, or a technical reviewer can open the live URL and see the eval dashboard without needing to clone and run anything themselves. A portfolio project without a live demo is invisible.

---

## What was built

### README
**File:** `README.md`
**What it does:** Complete project documentation. Covers what the system does, how it works step by step, the evaluation dimensions, every dashboard screen, the tech stack, local development setup, deployment instructions for both Railway and Vercel, and the adversarial test categories. Replaces the placeholder README from phase 1.

### CORS Update
**File:** `backend/main.py`
**What it does:** Extended the CORS regex to also allow requests from `*.railway.app` domains, so the deployed frontend on Vercel can call the backend on Railway without being blocked.

### Railway Build Config
**File:** `backend/nixpacks.toml`
**What it does:** Tells Railway how to build the Python app — which Python version to install, how to install dependencies, and what command to start the server with. Without this file, Railway may misdetect the project structure.
**Key decisions made:**
- Uses `python311` from nixpkgs for a deterministic build
- Start command matches the Procfile: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Chart Size Fixes
**Files:** `frontend/components/ScoreTrendChart.tsx`, `frontend/components/CategoryBarChart.tsx`
**What it does:** Reduced chart heights from 240px/280px to 120px/140px, thinned the line stroke from 1.5px to 1px, and reduced bar size from 14px to 8px. Charts are now compact and don't dominate the page layout.

---

## How data flows through this phase

1. User opens the frontend URL (Vercel-hosted Next.js app)
2. Browser sends API requests to the Railway-hosted FastAPI backend
3. Railway backend reads from the SQLite database (pre-populated with 100 eval results)
4. Results flow back to the frontend and render in the dashboard

---

## Deployment Instructions

### Backend → Render (free)
1. Go to render.com → New Web Service → connect GitHub repo
2. Settings auto-detected from `render.yaml` at repo root
3. Add env var: `ANTHROPIC_API_KEY`
4. Deploy — build takes ~3 minutes, copies DB from repo
5. Copy the Render URL (e.g. `https://rufus-eval-engine-api.onrender.com`)

### Frontend → Vercel
1. Connect repo at vercel.com/new → root directory: `frontend`
2. Set env var: `NEXT_PUBLIC_API_URL=<railway-url>`
3. Deploy — Vercel auto-detects Next.js

---

## Tests written

No new unit tests were added in this phase — the phase is primarily configuration and deployment. All backend and frontend tests from phases 7 and 8 continue to pass.

---

## Checkpoint verification

- ✓ README updated with live URLs placeholder and full setup guide
- ✓ Backend CORS allows `*.railway.app` and `*.vercel.app`
- ✓ `Procfile` uses `0.0.0.0` and `$PORT` for Railway
- ✓ `nixpacks.toml` created for Railway build detection
- ✓ 100 eval results in SQLite (pre-populated from prior phases)
- ✓ `docs/phase-9.md` generated
- ⏳ Live Railway URL — pending user deployment
- ⏳ Live Vercel URL — pending user deployment

---

## Known limitations

The SQLite database is bundled with the deployed backend. This works fine for a portfolio demo but would not scale to a multi-instance production setup — a hosted database (e.g., PostgreSQL on Railway) would be needed for that.

---

## What comes next

The project is complete. The next step is adding live URLs to the README once deployment is done, and optionally running a live eval batch (`USE_MOCK=false`) to populate fresh data in the production database.
