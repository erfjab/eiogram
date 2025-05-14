from typing import Callable, Awaitable, Union, TypeVar
from functools import wraps
import inspect

from ._base import BaseHandler
from ...types import Callback
from ...utils._filters import Filter
from ...utils._callback_data import CallbackDataFilter

CallbackT = TypeVar("CallbackT", bound=Callback)
CallbackHandler = Callable[[CallbackT], Awaitable[None]]
FilterFunc = Union[Filter, Callable[[Callback], bool], CallbackDataFilter]


class CallbackHandler(BaseHandler):
    def __init__(self):
        super().__init__(update_type="callback")

    def __call__(
        self, *filters: FilterFunc, priority: int = 0
    ) -> Callable[[CallbackHandler], CallbackHandler]:
        def decorator(func: CallbackHandler) -> CallbackHandler:
            sig = inspect.signature(func)
            wants_callback_data = "callback_data" in sig.parameters

            @wraps(func)
            async def wrapper(callback: Callback):
                callback_data = None

                for flt in filters:
                    result = flt(callback)
                    if inspect.isawaitable(result):
                        result = await result

                    if isinstance(result, bool):
                        if not result:
                            return
                    elif isinstance(flt, CallbackDataFilter):
                        callback_data = result

                if wants_callback_data and callback_data is not None:
                    return await func(callback, callback_data=callback_data)
                return await func(callback)

            self.register(handler=wrapper, filters=list(filters), priority=priority)
            return func

        return decorator
