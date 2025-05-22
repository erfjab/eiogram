from typing import Any, Dict, Optional, Union
from ._base import BaseStorage


class MemoryStorage(BaseStorage):
    def __init__(self):
        self._storage: Dict[Union[int, str], Dict[str, Any]] = {}

    async def get_stats(self, key: Union[int, str]) -> Optional[Dict[str, Any]]:
        return self._storage.get(key, {}).get("stats")

    async def set_stats(self, key: Union[int, str], stats: Dict[str, Any]) -> None:
        if key not in self._storage:
            self._storage[key] = {}
        self._storage[key]["stats"] = stats

    async def clear(self, key: Union[int, str]) -> None:
        if key in self._storage:
            del self._storage[key]

    async def upsert_data(self, key: Union[int, str], **data: Any) -> None:
        if key not in self._storage:
            self._storage[key] = {}
        if "data" not in self._storage[key]:
            self._storage[key]["data"] = {}
        self._storage[key]["data"].update(data)

    async def get_data(self, key: Union[int, str]) -> Dict[str, Any]:
        if key not in self._storage:
            return {}
        return self._storage[key].get("data", {})
