from dataclasses import dataclass
from typing import Callable, List, Optional, TypeVar, Union, Awaitable

from ...types import Update, Message, Callback
from ...utils._filters import Filter

U = TypeVar("U", bound=Union[Update, Message, Callback])
HandlerFunc = Callable[[U], Awaitable[None]]
FilterFunc = Union[Filter, Callable[[U], bool]]


@dataclass
class Handler:
    callback: HandlerFunc
    filters: List[FilterFunc]
    priority: int = 0


class BaseHandler:
    def __init__(self, update_type: str):
        self.update_type = update_type
        self.handlers: List[Handler] = []

    def register(
        self,
        handler: HandlerFunc,
        filters: Optional[List[FilterFunc]] = None,
        priority: int = 0,
    ) -> None:
        handler_entry = Handler(
            callback=handler, filters=filters or [], priority=priority
        )
        self.handlers.append(handler_entry)
        self.handlers.sort(key=lambda x: x.priority, reverse=True)

    def __call__(
        self, *filters: FilterFunc, priority: int = 0
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        def decorator(func: HandlerFunc) -> HandlerFunc:
            self.register(handler=func, filters=list(filters), priority=priority)
            return func

        return decorator
