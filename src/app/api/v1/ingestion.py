from datetime import datetime

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.infrastructure.arxiv import ArxivClient

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


class PaperPreview(BaseModel):
    arxiv_id: str
    title: str
    summary: str
    authors: tuple[str, ...]
    published_at: datetime
    updated_at: datetime
    pdf_url: str


@router.get("/preview", response_model=list[PaperPreview])
async def preview_ingestion(
    query: str = Query(min_length=1, description="An arXiv search query, for example cat:cs.AI"),
    max_results: int = Query(default=5, ge=1, le=100),
) -> list[PaperPreview]:
    client = ArxivClient()
    try:
        papers = await client.fetch(query, max_results)
    finally:
        await client.aclose()
    return [PaperPreview.model_validate(paper, from_attributes=True) for paper in papers]