import inspect
from functools import lru_cache
from typing import Optional, Union, Tuple
from ._handlers import (
    MessageHandler,
    CallbackQueryHandler,
    ErrorHandler,
    Handler,
)
from ..types import Update
from ..filters import StatsFilter
from ._dispatcher import Dispatcher
from ._handlers._middleware import MiddlewareHandler


class Router:
    def __init__(self, name: Optional[str] = None):
        self.name = name or f"router_{id(self)}"
        self.message = MessageHandler()
        self.callback_query = CallbackQueryHandler()
        self.middleware = MiddlewareHandler()
        self.error = ErrorHandler()
        self._parent_dispatcher: Optional[Dispatcher] = None

    def include_router(self, router: "Router") -> None:
        self.message.handlers.extend(router.message.handlers)
        self.callback_query.handlers.extend(router.callback_query.handlers)
        self.middleware.middlewares.extend(router.middleware.middlewares)
        self.error.handlers.extend(router.error.handlers)

    def setup(self, dispatcher: Dispatcher) -> None:
        self._parent_dispatcher = dispatcher

        # Register middlewares
        if self.middleware.middlewares:
            dispatcher.middlewares.extend(self.middleware.middlewares)
            dispatcher.middlewares.sort(key=lambda m: m.priority, reverse=True)

        # Register handlers
        for handler in self.message.handlers:
            dispatcher.register(
                update_type="message",
                handler=handler.callback,
                filters=handler.filters,
                priority=handler.priority,
            )

        for handler in self.callback_query.handlers:
            dispatcher.register(
                update_type="callback_query",
                handler=handler.callback,
                filters=handler.filters,
                priority=handler.priority,
            )

        # Register error handlers
        for handler in self.error.handlers:
            dispatcher.error.handlers.append(handler)

    @lru_cache(maxsize=None)
    def _get_handlers(self, is_message: bool) -> Tuple[Handler, ...]:
        """Get handlers with caching based on update type"""
        handlers = self.message.handlers if is_message else self.callback_query.handlers
        return tuple(handlers)

    @lru_cache(maxsize=None)
    def _get_non_stats_handlers(
        self, handlers_tuple: Tuple[Handler, ...]
    ) -> Tuple[Handler, ...]:
        """Get handlers without StatsFilter with caching"""
        return tuple(
            handler
            for handler in handlers_tuple
            if not any(isinstance(f, StatsFilter) for f in handler.filters)
        )

    @lru_cache(maxsize=None)
    def _get_stats_handlers(
        self, handlers_tuple: Tuple[Handler, ...]
    ) -> Tuple[Handler, ...]:
        """Get handlers with StatsFilter with caching"""
        return tuple(
            handler
            for handler in handlers_tuple
            if any(isinstance(f, StatsFilter) for f in handler.filters)
        )

    async def matches_update(self, update: Update) -> Union[bool, Handler]:
        is_message = update.message is not None
        handlers_tuple = self._get_handlers(is_message)

        if not handlers_tuple:
            return False

        stats = await self._parent_dispatcher.storage.get_stats(
            update.origin.from_user.chatid
        )

        if stats:
            filtered_handlers = self._get_stats_handlers(handlers_tuple)
        else:
            filtered_handlers = self._get_non_stats_handlers(handlers_tuple)

        if not filtered_handlers:
            return False

        for handler in filtered_handlers:
            if not handler.filters:
                return handler

            filter_passed = True
            for filter_func in handler.filters:
                if isinstance(filter_func, StatsFilter):
                    result = filter_func(stats)
                elif inspect.iscoroutinefunction(filter_func):
                    result = await filter_func(update.origin)
                else:
                    result = filter_func(update.origin)

                if not result:
                    filter_passed = False
                    break

            if filter_passed:
                return handler

        return False
