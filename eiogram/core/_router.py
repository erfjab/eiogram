import inspect
from typing import Optional, Union
from ._handlers import (
    MessageHandler,
    CallbackHandler,
    ErrorHandler,
    Handler,
)
from ..types import Update
from ..filters import StatsFilter
from ._dispatcher import Dispatcher
from ._handlers._middleware import MiddlewareHandler


class Router:
    def __init__(self, name: str = None):
        self.name = name or f"router_{id(self)}"
        self.message = MessageHandler()
        self.callback = CallbackHandler()
        self.middleware = MiddlewareHandler()
        self.error = ErrorHandler()
        self._parent_dispatcher: Optional[Dispatcher] = None

    def include_router(self, router: "Router") -> None:
        self.message.handlers.extend(router.message.handlers)
        self.callback.handlers.extend(router.callback.handlers)
        self.middleware.middlewares.extend(router.middleware.middlewares)
        self.error.handlers.extend(router.error.handlers)

    def setup(self, dispatcher: Dispatcher) -> None:
        self._parent_dispatcher = dispatcher

        # Register middlewares
        for mw in self.middleware.middlewares:
            dispatcher.middlewares.append(mw)
        dispatcher.middlewares.sort(key=lambda m: m.priority, reverse=True)

        # Register handlers
        for handler in self.message.handlers:
            dispatcher.register(
                update_type="message",
                handler=handler.callback,
                filters=handler.filters,
                priority=handler.priority,
            )

        for handler in self.callback.handlers:
            dispatcher.register(
                update_type="callback",
                handler=handler.callback,
                filters=handler.filters,
                priority=handler.priority,
            )

        # Register error handlers
        for handler in self.error.handlers:
            dispatcher.error.handlers.append(handler)

    async def matches_update(self, update: Update) -> Union[bool, Handler]:
        try:
            handlers = (
                self.message.handlers if update.message else self.callback.handlers
            )
            stats = await self._parent_dispatcher.storage.get_stats(
                update.origin.from_user.chatid
            )

            for handler in handlers:
                filter_results = []
                skip = False

                if stats and not any(
                    isinstance(f, StatsFilter) for f in handler.filters
                ):
                    continue

                if not handler.filters and not stats:
                    return handler

                for filter_func in handler.filters:
                    try:
                        result = filter_func(update.origin)
                        if inspect.isawaitable(result):
                            result = await result

                        if isinstance(result, bool):
                            if not result:
                                skip = True
                                break
                            filter_results.append(result)
                        else:
                            filter_results.append(True)
                    except Exception as e:
                        raise ValueError(f"Filter evaluation failed: {str(e)}") from e

                if not skip and all(filter_results):
                    return handler

            return False
        except Exception as e:
            raise RuntimeError(f"Update matching failed: {str(e)}") from e
