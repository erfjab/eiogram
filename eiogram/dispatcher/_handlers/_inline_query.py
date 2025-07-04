from typing import Callable, Awaitable, Union, TypeVar
from ._base import BaseHandler
from ...types import InlineQuery
from ...filters import Filter

InlineQueryT = TypeVar("InlineQueryT", bound=InlineQuery)
InlineQueryHandlerFunc = Callable[[InlineQueryT], Awaitable[None]]
FilterFunc = Union[Filter, Callable[[InlineQuery], Union[bool, Awaitable[bool]]]]


class InlineQueryHandler(BaseHandler):
    def __init__(self):
        super().__init__(update_type="inline_query")

    def __call__(self, *filters: FilterFunc, priority: int = 0) -> Callable[[InlineQueryHandlerFunc], InlineQueryHandlerFunc]:
        def decorator(func: InlineQueryHandlerFunc) -> InlineQueryHandlerFunc:
            return self.register(func, list(filters), priority)

        return decorator
