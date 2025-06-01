from typing import Optional, Union, Any, Dict
from .storage import BaseStorage, MemoryStorage
from ._stats import State


class StatsManager:
    def __init__(self, key: Union[int, str], storage: BaseStorage = MemoryStorage()):
        self.storage = storage
        self.key = key

    async def set_state(self, state: State) -> None:
        await self.storage.set_stats(self.key, stats=state.name)

    async def get_state(self) -> Optional[State]:
        return await self.storage.get_stats(self.key)

    async def upsert_data(self, **data: Any) -> None:
        return await self.storage.upsert_data(self.key, **data)

    async def get_data(self) -> Dict[str, Any]:
        return await self.storage.get_data(self.key)

    async def clear_all(self) -> None:
        await self.storage.clear_all(self.key)

    async def clear_stats(self) -> None:
        await self.storage.clear_stats(self.key)

    async def clear_data(self) -> None:
        await self.storage.clear_data(self.key)
