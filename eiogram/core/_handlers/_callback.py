import inspect
from functools import wraps
from typing import Callable, Awaitable, Union, TypeVar

from ._base import BaseHandler
from ...types import Callback
from ...filters import Filter
from ...utils._callback_data import CallbackDataFilter

CallbackT = TypeVar("CallbackT", bound=Callback)
CallbackHandler = Callable[[CallbackT], Awaitable[None]]
FilterFunc = Union[
    Filter, Callable[[Callback], Union[bool, Awaitable[bool]]], CallbackDataFilter
]


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
                filter_results = []

                for flt in filters:
                    try:
                        result = flt(callback)
                        if inspect.isawaitable(result):
                            result = await result

                        if isinstance(result, bool):
                            if not result:
                                return
                            filter_results.append(result)
                        elif isinstance(flt, CallbackDataFilter):
                            callback_data = result
                    except Exception as e:
                        raise ValueError(f"Filter error: {str(e)}") from e

                if wants_callback_data and callback_data is not None:
                    return await func(callback, callback_data=callback_data)
                return await func(callback)

            return self.register(wrapper, list(filters), priority)

        return decorator
