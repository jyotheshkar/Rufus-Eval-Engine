# Phase 7 tests — verifies all FastAPI endpoints return correct shapes and handle edge cases

import asyncio
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator

import aiosqlite
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Set DB path before importing app so the routes use the real DB
os.environ.setdefault("USE_MOCK", "true")

DB_PATH = Path(__file__).parent.parent / "data" / "eval_results.db"


@pytest.fixture(scope="module")
def event_loop():
    """Create a module-scoped event loop for all async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Fixtures — real DB (seeded by run_eval.py --mock --limit 20)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="module")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient connected to the FastAPI app using the real DB."""
    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Fixtures — empty DB (isolated temp file)
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="module")
async def empty_db_client() -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient connected to the FastAPI app with a fresh empty DB."""
    import backend.routes.evals as evals_mod
    import backend.routes.stats as stats_mod
    import backend.routes.adversarial as adv_mod
    from backend.evaluation.anomaly import init_db

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    await init_db(db_path=str(tmp_path))

    # Patch DB_PATH in all route modules for this fixture's scope
    original_evals = evals_mod.DB_PATH
    original_stats = stats_mod.DB_PATH
    original_adv = adv_mod.DB_PATH

    evals_mod.DB_PATH = tmp_path
    stats_mod.DB_PATH = tmp_path
    adv_mod.DB_PATH = tmp_path

    from backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    evals_mod.DB_PATH = original_evals
    stats_mod.DB_PATH = original_stats
    adv_mod.DB_PATH = original_adv
    tmp_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="module")
async def test_health_returns_200_with_ok_status(client: AsyncClient) -> None:
    """GET /health returns HTTP 200 with status='ok'."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "total_evals" in data
    assert "last_run" in data


# ---------------------------------------------------------------------------
# GET /evals
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="module")
async def test_list_evals_returns_200_with_correct_shape(client: AsyncClient) -> None:
    """GET /evals returns HTTP 200 with total, page, and results keys."""
    response = await client.get("/evals")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "page" in data
    assert "results" in data
    assert isinstance(data["results"], list)


@pytest.mark.asyncio(loop_scope="module")
async def test_list_evals_page_two_differs_from_page_one(client: AsyncClient) -> None:
    """GET /evals?page=2 returns different results than page=1, or empty list if fewer than limit."""
    r1 = await client.get("/evals?page=1&limit=10")
    r2 = await client.get("/evals?page=2&limit=10")
    assert r1.status_code == 200
    assert r2.status_code == 200
    d1 = r1.json()
    d2 = r2.json()
    # If total <= 10 then page 2 should be empty; otherwise results should differ
    if d1["total"] <= 10:
        assert d2["results"] == []
    else:
        ids1 = {r["id"] for r in d1["results"]}
        ids2 = {r["id"] for r in d2["results"]}
        assert ids1.isdisjoint(ids2), "Page 1 and page 2 must contain different records"


@pytest.mark.asyncio(loop_scope="module")
async def test_list_evals_result_has_required_fields(client: AsyncClient) -> None:
    """Each eval result in the list contains all required fields."""
    response = await client.get("/evals?limit=1")
    assert response.status_code == 200
    data = response.json()
    if data["results"]:
        result = data["results"][0]
        required_fields = {
            "id", "timestamp", "question_id", "question_text", "category",
            "difficulty", "is_adversarial", "rufus_answer",
            "score_helpfulness", "score_accuracy", "score_hallucination",
            "score_safety", "score_overall", "anomaly_flagged",
        }
        for field in required_fields:
            assert field in result, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# GET /evals/{eval_id}
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="module")
async def test_get_eval_by_valid_id_returns_200(client: AsyncClient) -> None:
    """GET /evals/{valid_id} returns HTTP 200 with the correct eval record."""
    # Grab a real ID from the list
    list_resp = await client.get("/evals?limit=1")
    assert list_resp.status_code == 200
    results = list_resp.json()["results"]
    assert results, "DB must have at least one result for this test"
    valid_id = results[0]["id"]

    response = await client.get(f"/evals/{valid_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == valid_id


@pytest.mark.asyncio(loop_scope="module")
async def test_get_eval_by_bad_id_returns_404(client: AsyncClient) -> None:
    """GET /evals/{bad_id} returns HTTP 404."""
    response = await client.get("/evals/nonexistent-id-xyz-999")
    assert response.status_code == 404
    assert "detail" in response.json()


# ---------------------------------------------------------------------------
# GET /stats/overview
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="module")
async def test_stats_overview_returns_200_with_all_keys(client: AsyncClient) -> None:
    """GET /stats/overview returns HTTP 200 with all required keys."""
    response = await client.get("/stats/overview")
    assert response.status_code == 200
    data = response.json()
    required_keys = {
        "total_evals", "avg_overall", "avg_helpfulness", "avg_accuracy",
        "avg_hallucination", "avg_safety", "anomaly_count", "worst_category",
    }
    for key in required_keys:
        assert key in data, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# GET /stats/by-category
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="module")
async def test_stats_by_category_returns_list(client: AsyncClient) -> None:
    """GET /stats/by-category returns a list of category stats."""
    response = await client.get("/stats/by-category")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "category" in data[0]
        assert "avg_overall" in data[0]
        assert "count" in data[0]


# ---------------------------------------------------------------------------
# GET /stats/trend
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="module")
async def test_stats_trend_returns_list(client: AsyncClient) -> None:
    """GET /stats/trend returns a list of trend points."""
    response = await client.get("/stats/trend")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "date" in data[0]
        assert "avg_overall" in data[0]


@pytest.mark.asyncio(loop_scope="module")
async def test_stats_trend_respects_days_param(client: AsyncClient) -> None:
    """GET /stats/trend?days=1 returns a list (may be empty if no evals today)."""
    response = await client.get("/stats/trend?days=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ---------------------------------------------------------------------------
# GET /stats/anomalies
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="module")
async def test_stats_anomalies_returns_list(client: AsyncClient) -> None:
    """GET /stats/anomalies returns a list of anomaly items."""
    response = await client.get("/stats/anomalies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "eval_id" in data[0]
        assert "score_overall" in data[0]
        assert "anomaly_reason" in data[0]


# ---------------------------------------------------------------------------
# GET /adversarial/summary
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="module")
async def test_adversarial_summary_returns_correct_shape(client: AsyncClient) -> None:
    """GET /adversarial/summary returns correct shape with total field."""
    response = await client.get("/adversarial/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "by_category" in data
    assert isinstance(data["by_category"], list)


# ---------------------------------------------------------------------------
# Empty DB — all endpoints return 200 (not errors) on empty database
# ---------------------------------------------------------------------------

@pytest.mark.asyncio(loop_scope="module")
async def test_empty_db_health_returns_200(empty_db_client: AsyncClient) -> None:
    """GET /health returns 200 with total_evals=0 on empty DB."""
    response = await empty_db_client.get("/health")
    assert response.status_code == 200
    assert response.json()["total_evals"] == 0


@pytest.mark.asyncio(loop_scope="module")
async def test_empty_db_list_evals_returns_empty(empty_db_client: AsyncClient) -> None:
    """GET /evals returns total=0, results=[] on empty DB."""
    response = await empty_db_client.get("/evals")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []


@pytest.mark.asyncio(loop_scope="module")
async def test_empty_db_overview_returns_zeros(empty_db_client: AsyncClient) -> None:
    """GET /stats/overview returns zeros on empty DB, not an error."""
    response = await empty_db_client.get("/stats/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_evals"] == 0
    assert data["avg_overall"] == 0.0


@pytest.mark.asyncio(loop_scope="module")
async def test_empty_db_by_category_returns_empty_list(empty_db_client: AsyncClient) -> None:
    """GET /stats/by-category returns [] on empty DB."""
    response = await empty_db_client.get("/stats/by-category")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="module")
async def test_empty_db_trend_returns_empty_list(empty_db_client: AsyncClient) -> None:
    """GET /stats/trend returns [] on empty DB."""
    response = await empty_db_client.get("/stats/trend")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="module")
async def test_empty_db_anomalies_returns_empty_list(empty_db_client: AsyncClient) -> None:
    """GET /stats/anomalies returns [] on empty DB."""
    response = await empty_db_client.get("/stats/anomalies")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio(loop_scope="module")
async def test_empty_db_adversarial_summary_returns_zeros(empty_db_client: AsyncClient) -> None:
    """GET /adversarial/summary returns total=0, by_category=[] on empty DB."""
    response = await empty_db_client.get("/adversarial/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["by_category"] == []
