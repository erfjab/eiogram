import inspect
from typing import Optional, Union
from .handlers import (
    MessageHandler,
    CallbackHandler,
    MiddlewareHandler,
    ErrorHandler,
    Handler,
)
from ..types import Update
from ..utils._filters import StatsFilter
from ._dispatcher import Dispatcher


class Router:
    def __init__(self, name: str = None):
        self.name = name or f"router_{id(self)}"
        self.message = MessageHandler()
        self.callback = CallbackHandler()
        self.middleware = MiddlewareHandler()
        self.error = ErrorHandler()
        self._parent_dispatcher: Optional["Dispatcher"] = None

    def include_router(self, router: "Router") -> None:
        self.message.handlers.extend(router.message.handlers)
        self.callback.handlers.extend(router.callback.handlers)
        self.middleware.middlewares.extend(router.middleware.middlewares)
        self.error.handlers.extend(router.error.handlers)

    def setup(self, dispatcher: "Dispatcher") -> None:
        self._parent_dispatcher = dispatcher

        # Register middlewares
        for mw in self.middleware.middlewares:
            dispatcher.middlewares.append(mw)
            dispatcher.middlewares.sort(key=lambda m: m.priority, reverse=True)

        # Register message handlers
        for handler in self.message.handlers:
            dispatcher.register(
                update_type="message",
                handler=handler.callback,
                filters=handler.filters,
                priority=handler.priority,
            )

        # Register callback handlers
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

    async def _process_middlewares(self, update: Update) -> Optional[Update]:
        current_data = update
        for mw in self.middleware.middlewares:
            try:
                current_data = await mw.func(current_data)
                if current_data is None:
                    return None
            except Exception as e:
                if not await self.error.handle(e):
                    raise
        return current_data

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

                if stats and not any(
                    isinstance(f, StatsFilter) for f in handler.filters
                ):
                    continue

                if not handler.filters and not stats:
                    return handler

                for filter_func in handler.filters:
                    try:
                        if isinstance(filter_func, StatsFilter):
                            result = filter_func(stats)
                        elif inspect.iscoroutinefunction(filter_func):
                            result = await filter_func(update.origin)
                        else:
                            result = filter_func(update.origin)

                        filter_results.append(result)
                    except Exception as e:
                        if not await self.error.handle(e):
                            raise

                if all(filter_results):
                    return handler

            return False
        except Exception as e:
            if not await self.error.handle(e):
                raise
            return False
