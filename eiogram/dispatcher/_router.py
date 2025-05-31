import inspect
from typing import Optional, Tuple, Union
from functools import lru_cache
from ._handlers import (
    MessageHandler,
    CallbackQueryHandler,
    MiddlewareHandler,
    Handler,
)
from ..types import Update
from ..filters import StatsFilter
from ..stats import State


class Router:
    def __init__(self, name: Optional[str] = None):
        self.name = name or f"router_{id(self)}"
        self.message = MessageHandler()
        self.callback_query = CallbackQueryHandler()
        self.middleware = MiddlewareHandler()

    def include_router(self, router: "Router") -> None:
        self.message.handlers.extend(router.message.handlers)
        self.callback_query.handlers.extend(router.callback_query.handlers)
        self.middleware.middlewares.extend(router.middleware.middlewares)

    @lru_cache(maxsize=None)
    def _get_handlers(self, is_message: bool) -> Tuple[Handler]:
        """Get handlers with caching based on update type"""
        handlers = self.message.handlers if is_message else self.callback_query.handlers
        return tuple(handlers)

    @lru_cache(maxsize=None)
    def _get_non_stats_handlers(self, handlers_tuple: Tuple[Handler]) -> Tuple[Handler]:
        """Get handlers without StatsFilter with caching"""
        return tuple(
            handler
            for handler in handlers_tuple
            if not any(isinstance(f, StatsFilter) for f in handler.filters)
        )

    @lru_cache(maxsize=None)
    def _get_stats_handlers(self, handlers_tuple: Tuple[Handler]) -> Tuple[Handler]:
        """Get handlers with StatsFilter with caching"""
        return tuple(
            handler
            for handler in handlers_tuple
            if any(isinstance(f, StatsFilter) for f in handler.filters)
        )

    async def matches_update(
        self, update: Update, stats: Optional[State] = None
    ) -> Union[bool, Handler]:
        is_message = update.message is not None
        handlers_tuple = self._get_handlers(is_message)

        if not handlers_tuple:
            return False

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
