from typing import Any, Callable, Dict, Awaitable
from abc import ABC, abstractmethod
from ..types import Update


class BaseMiddleware(ABC):
    def __init__(self, priority: int = 0):
        self.priority = priority

    @abstractmethod
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        update: Update,
        data: Dict[str, Any],
    ) -> Any:
        pass
