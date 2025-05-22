from typing import Callable, Awaitable, Union, TypeVar

from ._base import BaseHandler
from ...types import Callback
from ...filters import Filter

CallbackT = TypeVar("CallbackT", bound=Callback)
CallbackHandlerFunc = Callable[[CallbackT], Awaitable[None]]
FilterFunc = Union[Filter, Callable[[Callback], Union[bool, Awaitable[bool]]]]


class CallbackHandler(BaseHandler):
    def __init__(self):
        super().__init__(update_type="callback")

    def __call__(
        self, *filters: FilterFunc, priority: int = 0
    ) -> Callable[[CallbackHandlerFunc], CallbackHandlerFunc]:
        def decorator(func: CallbackHandler) -> CallbackHandler:
            return self.register(func, list(filters), priority)

        return decorator
