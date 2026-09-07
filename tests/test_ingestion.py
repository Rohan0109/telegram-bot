from datetime import UTC, datetime

import httpx

from app.domain.papers import Paper
from app.infrastructure.arxiv import ArxivClient
from app.services.ingestion import PaperIngestionService


class FakeSource:
    def __init__(self, papers: list[Paper]) -> None:
        self.papers = papers

    async def fetch(self, query: str, max_results: int = 100) -> list[Paper]:
        assert query == "cat:cs.AI"
        assert max_results == 10
        return self.papers


class InMemoryPaperRepository:
    def __init__(self, papers: list[Paper] | None = None) -> None:
        self.papers = {paper.arxiv_id: paper for paper in papers or []}

    async def get_by_arxiv_id(self, arxiv_id: str) -> Paper | None:
        return self.papers.get(arxiv_id)

    async def save(self, paper: Paper) -> Paper:
        self.papers[paper.arxiv_id] = paper
        return paper


def make_paper(title: str = "A paper") -> Paper:
    published_at = datetime(2026, 1, 1, tzinfo=UTC)
    return Paper(
        arxiv_id="2601.00001",
        title=title,
        summary="Summary",
        authors=("Author",),
        published_at=published_at,
        updated_at=published_at,
        pdf_url="https://arxiv.org/pdf/2601.00001",
    )


async def test_sync_stores_new_papers_and_skips_unchanged_papers() -> None:
    paper = make_paper()
    repository = InMemoryPaperRepository([paper])
    service = PaperIngestionService(FakeSource([paper]), repository)

    result = await service.sync("cat:cs.AI", max_results=10)

    assert result.fetched == 1
    assert result.stored == 0
    assert result.skipped == 1


async def test_sync_updates_existing_paper() -> None:
    old_paper = make_paper()
    new_paper = make_paper(title="Updated title")
    repository = InMemoryPaperRepository([old_paper])
    service = PaperIngestionService(FakeSource([new_paper]), repository)

    result = await service.sync("cat:cs.AI", max_results=10)

    assert result.stored == 1
    assert result.skipped == 0
    assert repository.papers[old_paper.arxiv_id].title == "Updated title"


async def test_arxiv_client_parses_atom_feed() -> None:
        feed = """
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <id>http://arxiv.org/abs/2601.00001v1</id>
                <title>  A paper about retrieval  </title>
                <summary> A short summary. </summary>
                <author><name>Author One</name></author>
                <published>2026-01-01T00:00:00Z</published>
                <updated>2026-01-02T00:00:00Z</updated>
                <link title="pdf" href="https://arxiv.org/pdf/2601.00001" />
            </entry>
        </feed>
        """

        async def handler(request: httpx.Request) -> httpx.Response:
                assert request.url.params["search_query"] == "cat:cs.AI"
                return httpx.Response(200, text=feed)

        client = ArxivClient(httpx.AsyncClient(transport=httpx.MockTransport(handler)))
        papers = await client.fetch("cat:cs.AI", max_results=10)

        assert papers[0].arxiv_id == "2601.00001"
        assert papers[0].title == "A paper about retrieval"
        assert papers[0].authors == ("Author One",)
        assert papers[0].published_at == datetime(2026, 1, 1, tzinfo=UTC)
        assert papers[0].pdf_url == "https://arxiv.org/pdf/2601.00001"