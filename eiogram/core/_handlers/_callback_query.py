from typing import Callable, Awaitable, Union, TypeVar

from ._base import BaseHandler
from ...types import Callback
from ...filters import Filter

CallbackQueryT = TypeVar("CallbackQueryT", bound=Callback)
CallbackQueryHandlerFunc = Callable[[CallbackQueryT], Awaitable[None]]
FilterFunc = Union[Filter, Callable[[Callback], Union[bool, Awaitable[bool]]]]


class CallbackQueryHandler(BaseHandler):
    def __init__(self):
        super().__init__(update_type="callback_query")

    def __call__(
        self, *filters: FilterFunc, priority: int = 0
    ) -> Callable[[CallbackQueryHandlerFunc], CallbackQueryHandlerFunc]:
        def decorator(func: CallbackQueryHandler) -> CallbackQueryHandler:
            return self.register(func, list(filters), priority)

        return decorator
