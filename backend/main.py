# FastAPI application entry point — mounts all routers and configures middleware

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.adversarial import router as adversarial_router
from backend.routes.data import router as data_router
from backend.routes.evals import router as evals_router
from backend.routes.stats import router as stats_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Rufus Eval Engine API",
    description="LLM evaluation framework for the Rufus AI shopping assistant",
    version="1.0.0",
)

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"(https://.*\.vercel\.app|https://.*\.railway\.app|http://(localhost|127\.0\.0\.1):3000)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evals_router)
app.include_router(stats_router)
app.include_router(adversarial_router)
app.include_router(data_router)


@app.get("/")
async def root():
    """Root endpoint — confirms the API is running."""
    return {"name": "Rufus Eval Engine API", "version": "1.0.0", "status": "running"}


logger.info("Rufus Eval Engine API started")
