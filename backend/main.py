# FastAPI application entry point — mounts all routers and configures middleware

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.adversarial import router as adversarial_router
from backend.routes.evals import router as evals_router
from backend.routes.stats import router as stats_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Rufus Eval Engine API",
    description="LLM evaluation framework for the Rufus AI shopping assistant",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(evals_router)
app.include_router(stats_router)
app.include_router(adversarial_router)

logger.info("Rufus Eval Engine API started")
