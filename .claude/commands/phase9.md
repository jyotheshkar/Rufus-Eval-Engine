# Phase 9 — Integration + Deployment

## Goal
Wire everything together, run a real API evaluation, deploy backend to Railway
and frontend to Vercel. This is the only phase where `USE_MOCK=false` is used.

---

## API budget allocation for this phase

| Run | Questions | Est. cost |
|-----|-----------|-----------|
| Test run (standard) | 20 | ~$0.30 |
| Adversarial run | 10 | ~$0.15 |
| Full standard run | 100 | ~$1.50 |
| **Total** | **130** | **~$1.95** |

Confirm budget remaining before running. Do not exceed $10 total project budget.

---

## Step 1 — Run real evaluation (first live API call)

```bash
USE_MOCK=false python backend/scripts/run_eval.py --count 20 --mode standard
```

Watch costs. 20 questions should cost under $0.50.
Verify results saved to SQLite:

```bash
python -c "
import sqlite3
conn = sqlite3.connect('backend/data/eval_results.db')
rows = conn.execute('SELECT COUNT(*) FROM eval_results').fetchone()
print(f'Stored results: {rows[0]}')
"
```

---

## Step 2 — Run adversarial suite live

```bash
USE_MOCK=false python backend/scripts/run_adversarial.py --count 10
```

10 adversarial queries. Verify failure modes detected correctly in results.

---

## Step 3 — Run full standard eval

```bash
USE_MOCK=false python backend/scripts/run_eval.py --count 100 --mode standard
```

100 questions. ~$1.50. Verify all 100 stored in SQLite.
Check dashboard shows correct data before deploying.

---

## Step 4 — Deploy backend to Railway

1. Create Railway account at railway.app
2. New project → Deploy from GitHub → select `rufus-eval-engine`
3. Set root directory: `/backend`
4. Add environment variables: `ANTHROPIC_API_KEY`, `USE_MOCK=false`, `ENVIRONMENT=production`
5. Railway auto-detects FastAPI via `requirements.txt` and deploys
6. Copy the Railway URL (e.g., `https://rufus-eval-engine.up.railway.app`)

---

## Step 5 — Deploy frontend to Vercel

1. Push all frontend code to `main` branch on GitHub
2. Connect repo to Vercel (vercel.com/new)
3. Set root directory: `/frontend`
4. Add environment variable: `NEXT_PUBLIC_API_URL = <your Railway URL>`
5. Deploy

---

## Step 6 — Final checks

- [ ] All 4 dashboard screens load in production (no console errors)
- [ ] API endpoints respond correctly from Railway URL
- [ ] Real eval data visible in the dashboard (not empty)
- [ ] Anomalies detected and flagged in the dashboard
- [ ] Adversarial report populated with failure modes
- [ ] README updated with live frontend URL and backend URL
- [ ] Total API spend verified under $10

---

## Phase 9 complete when:
- Live URLs working for both frontend and backend
- Real eval data visible in the deployed dashboard
- README has live demo link
- Total API budget not exceeded
- `docs/phase-9.md` generated
