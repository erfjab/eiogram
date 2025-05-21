from typing import Callable, Awaitable, TypeVar

from ._base import BaseHandler, FilterFunc
from ...types import Message

MessageT = TypeVar("MessageT", bound=Message)
MessageHandler = Callable[[MessageT], Awaitable[None]]


class MessageHandler(BaseHandler):
    def __init__(self):
        super().__init__(update_type="message")

    def __call__(
        self, *filters: FilterFunc, priority: int = 0
    ) -> Callable[[MessageHandler], MessageHandler]:
        return super().__call__(*filters, priority=priority)
