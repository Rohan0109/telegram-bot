from typing import Protocol

from app.domain.papers import Paper


class TelegramGateway(Protocol):
    async def send_message(self, chat_id: int, text: str) -> None:
        ...


class PaperSource(Protocol):
    async def fetch(self, query: str, max_results: int = 100) -> list[Paper]:
        ...


class PaperRepository(Protocol):
    async def get_by_arxiv_id(self, arxiv_id: str) -> Paper | None:
        ...

    async def save(self, paper: Paper) -> Paper:
        ...
