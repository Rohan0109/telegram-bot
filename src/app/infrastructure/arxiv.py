from datetime import datetime
from xml.etree import ElementTree

import httpx

from app.domain.papers import Paper

ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NAMESPACE = "http://www.w3.org/2005/Atom"


class ArxivClient:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(timeout=30.0)
        self._owns_client = client is None

    async def fetch(self, query: str, max_results: int = 100) -> list[Paper]:
        response = await self._client.get(
            ARXIV_API_URL,
            params={"search_query": query, "start": 0, "max_results": max_results},
        )
        response.raise_for_status()
        return _parse_feed(response.text)

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()


def _parse_feed(xml: str) -> list[Paper]:
    root = ElementTree.fromstring(xml)
    papers: list[Paper] = []

    for entry in root.findall(f"{{{ATOM_NAMESPACE}}}entry"):
        arxiv_id = _required_text(entry, "id").rsplit("/", maxsplit=1)[-1].rsplit("v", 1)[0]
        papers.append(
            Paper(
                arxiv_id=arxiv_id,
                title=_required_text(entry, "title"),
                summary=_required_text(entry, "summary"),
                authors=tuple(
                    _required_text(author, "name")
                    for author in entry.findall(f"{{{ATOM_NAMESPACE}}}author")
                ),
                published_at=_parse_datetime(_required_text(entry, "published")),
                updated_at=_parse_datetime(_required_text(entry, "updated")),
                pdf_url=_pdf_url(entry),
            )
        )

    return papers


def _required_text(element: ElementTree.Element, name: str) -> str:
    value = element.findtext(f"{{{ATOM_NAMESPACE}}}{name}")
    if value is None:
        raise ValueError(f"arXiv entry is missing {name}")
    return " ".join(value.split())


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _pdf_url(entry: ElementTree.Element) -> str:
    for link in entry.findall(f"{{{ATOM_NAMESPACE}}}link"):
        if link.attrib.get("title") == "pdf":
            return link.attrib["href"]
    raise ValueError("arXiv entry is missing a PDF link")