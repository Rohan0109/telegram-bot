from dataclasses import dataclass

from app.domain.ports import PaperRepository, PaperSource


@dataclass(frozen=True, slots=True)
class IngestionResult:
    fetched: int
    stored: int
    skipped: int


class PaperIngestionService:
    def __init__(self, source: PaperSource, repository: PaperRepository) -> None:
        self._source = source
        self._repository = repository

    async def sync(self, query: str, max_results: int = 100) -> IngestionResult:
        papers = await self._source.fetch(query, max_results)
        stored = 0
        skipped = 0

        for paper in papers:
            existing = await self._repository.get_by_arxiv_id(paper.arxiv_id)
            if existing == paper:
                skipped += 1
                continue
            await self._repository.save(paper)
            stored += 1

        return IngestionResult(fetched=len(papers), stored=stored, skipped=skipped)