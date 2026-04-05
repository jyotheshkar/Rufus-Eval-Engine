# Data routes — serve raw dataset files (products, questions, adversarial) for visualisation

import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data", tags=["data"])

DATA_DIR = Path(__file__).parent.parent / "data"


@router.get("/products")
async def get_products():
    """Return all products from products.json (without embeddings to reduce payload)."""
    try:
        with open(DATA_DIR / "products.json", "r", encoding="utf-8") as f:
            products = json.load(f)
        for p in products:
            p.pop("embedding", None)
        return products
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="products.json not found")
    except Exception as exc:
        logger.error("Failed to load products: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load products data")


@router.get("/questions")
async def get_questions():
    """Return all questions from questions.json."""
    try:
        with open(DATA_DIR / "questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="questions.json not found")
    except Exception as exc:
        logger.error("Failed to load questions: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load questions data")


@router.get("/adversarial")
async def get_adversarial():
    """Return all adversarial queries from adversarial.json."""
    try:
        with open(DATA_DIR / "adversarial.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="adversarial.json not found")
    except Exception as exc:
        logger.error("Failed to load adversarial data: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load adversarial data")
