from typing import Protocol


class TelegramGateway(Protocol):
    async def send_message(self, chat_id: int, text: str) -> None:
        ...
