from datetime import UTC, datetime

from httpx import ASGITransport, AsyncClient

from app.api.v1 import ingestion
from app.domain.papers import Paper
from app.main import app


async def test_preview_ingestion_returns_arxiv_metadata(monkeypatch) -> None:
    paper = Paper(
        arxiv_id="2601.00001",
        title="A paper",
        summary="Summary",
        authors=("Author",),
        published_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
        pdf_url="https://arxiv.org/pdf/2601.00001",
    )

    class FakeArxivClient:
        async def fetch(self, query: str, max_results: int) -> list[Paper]:
            assert query == "cat:cs.AI"
            assert max_results == 1
            return [paper]

        async def aclose(self) -> None:
            pass

    monkeypatch.setattr(ingestion, "ArxivClient", FakeArxivClient)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/api/v1/ingestion/preview",
            params={"query": "cat:cs.AI", "max_results": 1},
        )

    assert response.status_code == 200
    assert response.json()[0]["arxiv_id"] == "2601.00001"