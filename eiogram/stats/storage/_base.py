from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union


class BaseStorage(ABC):
    @abstractmethod
    async def get_stats(self, key: Union[int, str]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def set_stats(self, key: Union[int, str], stats: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def clear(self, key: Union[int, str]) -> None:
        pass

    @abstractmethod
    async def upsert_data(self, key: Union[int, str], **data: Any) -> None:
        pass

    @abstractmethod
    async def get_data(self, key: Union[int, str]) -> Dict[str, Any]:
        pass
