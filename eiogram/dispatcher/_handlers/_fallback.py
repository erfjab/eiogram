from typing import Callable, Awaitable, TypeVar, Optional
from ._base import BaseHandler
from ...types import Update

UpdateT = TypeVar("UpdateT", bound=Update)
FallbackHandlerFunc = Callable[[UpdateT], Awaitable[None]]


class FallbackHandler(BaseHandler):
    def __init__(self):
        super().__init__(update_type="fallback")
        self._handler: Optional[FallbackHandlerFunc] = None

    def __call__(self, handler: FallbackHandlerFunc) -> FallbackHandlerFunc:
        if self._handler is not None:
            raise ValueError("Only one fallback handler can be registered")

        self._handler = handler
        return handler

    @property
    def handler(self) -> Optional[FallbackHandlerFunc]:
        return self._handler
