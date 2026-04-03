# FAISS-based product retriever: embeds products, builds index, and returns top-k results for a query

import json
import logging
import os
import time
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"


def product_to_text(product: dict) -> str:
    """Convert a product dict into a single string for embedding."""
    specs = product.get("specs", {})
    spec_parts = []
    for k, v in specs.items():
        if v is None:
            continue
        if isinstance(v, list):
            spec_parts.append(f"{k}: {' '.join(str(x) for x in v)}")
        else:
            spec_parts.append(f"{k}: {v}")
    specs_str = " ".join(spec_parts)
    tags_str = " ".join(product.get("tags", []))
    return (
        f"{product['name']} {product['category']} "
        f"{product.get('description', '')} {specs_str} {tags_str}"
    )


class FAISSRetriever:
    """Loads products, builds a FAISS flat-L2 index, and serves top-k search results."""

    def __init__(self, products_path: str) -> None:
        self.products_path = Path(products_path)
        self.model = SentenceTransformer(MODEL_NAME)
        self.products: list[dict] = []
        self.index: faiss.IndexFlatL2 | None = None
        self.product_ids: list[str] = []
        self._load_products()

    def _load_products(self) -> None:
        """Load products from JSON file."""
        with open(self.products_path) as f:
            self.products = json.load(f)
        logger.info("Loaded %d products from %s", len(self.products), self.products_path)

    def build_index(self) -> None:
        """Embed all products and build the FAISS index."""
        logger.info("Embedding %d products with %s...", len(self.products), MODEL_NAME)
        texts = [product_to_text(p) for p in self.products]
        embeddings = self.model.encode(texts, show_progress_bar=True, batch_size=64)
        embeddings = embeddings.astype(np.float32)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        self.product_ids = [p["id"] for p in self.products]
        logger.info("FAISS index built: %d vectors, dimension %d", len(self.products), dimension)

        # Store embeddings back on products in memory
        for product, embedding in zip(self.products, embeddings):
            product["embedding"] = embedding.tolist()

    def save_index(self, index_dir: str) -> None:
        """Save FAISS index and product ID map to disk."""
        dir_path = Path(index_dir)
        dir_path.mkdir(parents=True, exist_ok=True)

        index_path = dir_path / "products.index"
        ids_path = dir_path / "product_ids.json"

        faiss.write_index(self.index, str(index_path))
        with open(ids_path, "w") as f:
            json.dump(self.product_ids, f)
        logger.info("Index saved to %s", dir_path)

    def load_index(self, index_dir: str) -> None:
        """Load a pre-built FAISS index and product ID map from disk."""
        dir_path = Path(index_dir)
        index_path = dir_path / "products.index"
        ids_path = dir_path / "product_ids.json"

        self.index = faiss.read_index(str(index_path))
        with open(ids_path) as f:
            self.product_ids = json.load(f)
        logger.info("Index loaded from %s (%d vectors)", dir_path, self.index.ntotal)

    def search(self, query: str, k: int = 5) -> list[dict]:
        """Embed a query and return the top-k most relevant products."""
        if self.index is None:
            raise RuntimeError("Index not built or loaded. Call build_index() or load_index() first.")

        query_embedding = self.model.encode([query], show_progress_bar=False).astype(np.float32)
        distances, indices = self.index.search(query_embedding, k)

        results = []
        id_to_product = {p["id"]: p for p in self.products}
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            product_id = self.product_ids[idx]
            product = id_to_product.get(product_id)
            if product:
                result = dict(product)
                result["_score"] = float(dist)
                results.append(result)
        return results
