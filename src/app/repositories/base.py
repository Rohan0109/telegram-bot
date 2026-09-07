from typing import Protocol, TypeVar

EntityT = TypeVar("EntityT")


class Repository(Protocol[EntityT]):
    async def get(self, entity_id: str) -> EntityT | None:
        ...

    async def save(self, entity: EntityT) -> EntityT:
        ...
