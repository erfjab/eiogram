from typing import Callable, Awaitable, Optional
from ...types import Update


class FallbackHandler:
    def __init__(self):
        self._handler: Optional[Callable[[Update], Awaitable[None]]] = None

    def __call__(self, handler: Callable[[Update], Awaitable[None]]) -> Callable:
        if self._handler is not None:
            raise ValueError("Only one fallback handler can be registered")
        self._handler = handler
        return handler

    @property
    def handler(self) -> Optional[Callable[[Update], Awaitable[None]]]:
        return self._handler
