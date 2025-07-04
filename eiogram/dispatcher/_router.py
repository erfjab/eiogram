import inspect
from typing import Optional, Tuple, Union, List, Dict
from functools import lru_cache
from enum import Enum, auto
from ._handlers import (
    MessageHandler,
    CallbackQueryHandler,
    MiddlewareHandler,
    InlineQueryHandler,
    Handler,
)
from ..types import Update
from ..filters import StatsFilter, IgnoreStatsFilter
from ..stats import State


class HandlerPriority(Enum):
    STATS_IGNORE = auto()
    STATS_REQUIRED = auto()
    STATS_INDEPENDENT = auto()


class Router:
    def __init__(self, name: Optional[str] = None):
        self.name = name or f"router_{id(self)}"
        self.message = MessageHandler()
        self.callback_query = CallbackQueryHandler()
        self.inline_query = InlineQueryHandler()
        self.middleware = MiddlewareHandler()

    def include_router(self, router: "Router") -> None:
        self.message.handlers.extend(router.message.handlers)
        self.callback_query.handlers.extend(router.callback_query.handlers)
        self.inline_query.handlers.extend(router.inline_query.handlers)
        self.middleware.middlewares.extend(router.middleware.middlewares)

    def _get_handlers(self, update: Update) -> Tuple[Handler]:
        if update.callback_query:
            return tuple(self.callback_query.handlers)
        if update.message:
            return tuple(self.message.handlers)
        if update.inline_query:
            return tuple(self.inline_query.handlers)
        return tuple()

    @lru_cache(maxsize=128)
    def _categorize_handlers(self, handlers: Tuple[Handler]) -> Dict[HandlerPriority, List[Handler]]:
        categorized = {
            HandlerPriority.STATS_IGNORE: [],
            HandlerPriority.STATS_REQUIRED: [],
            HandlerPriority.STATS_INDEPENDENT: [],
        }

        for handler in handlers:
            if any(isinstance(f, IgnoreStatsFilter) for f in handler.filters):
                categorized[HandlerPriority.STATS_IGNORE].append(handler)
            elif any(isinstance(f, StatsFilter) for f in handler.filters):
                categorized[HandlerPriority.STATS_REQUIRED].append(handler)
            else:
                categorized[HandlerPriority.STATS_INDEPENDENT].append(handler)

        return categorized

    @staticmethod
    def _get_relevant_priorities(stats: Optional[State]) -> List[HandlerPriority]:
        if stats is not None:
            return [HandlerPriority.STATS_IGNORE, HandlerPriority.STATS_REQUIRED]
        return [HandlerPriority.STATS_IGNORE, HandlerPriority.STATS_INDEPENDENT]

    async def matches_update(self, update: Update, stats: Optional[State] = None) -> Union[bool, Handler]:
        handlers = self._get_handlers(update)
        if not handlers:
            return False

        categorized = self._categorize_handlers(handlers)

        for priority in self._get_relevant_priorities(stats):
            for handler in categorized.get(priority, []):
                if await self._check_handler(handler, update, stats):
                    return handler

        return False

    async def _check_handler(
        self,
        handler: Handler,
        update: Update,
        stats: Optional[State],
    ) -> bool:
        for filter_func in handler.filters:
            if isinstance(filter_func, IgnoreStatsFilter):
                continue

            if isinstance(filter_func, StatsFilter):
                if not filter_func(stats):
                    return False
                continue

            result = (
                await filter_func(update.origin) if inspect.iscoroutinefunction(filter_func) else filter_func(update.origin)
            )
            if not result:
                return False

        return True
