from typing import Callable, List, Optional, TypeVar, Union, Awaitable
from ...types import Update, Message, CallbackQuery
from ...filters import Filter

U = TypeVar("U", bound=Union[Update, Message, CallbackQuery])
HandlerFunc = Callable[[U], Awaitable[None]]
FilterFunc = Union[Filter, Callable[[U], Union[bool, Awaitable[bool]]]]


class Handler:
    def __init__(self, callback, filters, priority=0):
        self.callback = callback
        self.filters = filters
        self.priority = priority

    def __hash__(self):
        return hash(
            (id(self.callback), tuple(id(f) for f in self.filters), self.priority)
        )

    def __eq__(self, other):
        if not isinstance(other, Handler):
            return False
        return (
            self.callback == other.callback
            and self.filters == other.filters
            and self.priority == other.priority
        )


class BaseHandler:
    def __init__(self, update_type: str):
        self.update_type = update_type
        self.handlers: List[Handler] = []

    def register(
        self,
        handler: HandlerFunc,
        filters: Optional[List[FilterFunc]] = None,
        priority: int = 0,
    ) -> HandlerFunc:
        handler_entry = Handler(
            callback=handler, filters=filters or [], priority=priority
        )
        self.handlers.append(handler_entry)
        self.handlers.sort(key=lambda x: x.priority, reverse=True)
        return handler

    def __call__(
        self, *filters: FilterFunc, priority: int = 0
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        def decorator(func: HandlerFunc) -> HandlerFunc:
            return self.register(func, list(filters), priority)

        return decorator
