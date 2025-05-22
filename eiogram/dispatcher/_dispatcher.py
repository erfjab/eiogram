import inspect
from typing import Optional, TypeVar, Union, List, Tuple, Callable, Dict, Any
from ._handlers import Handler, MiddlewareHandler
from ._router import Router
from ..client import Bot
from ..types import Update, Message, CallbackQuery
from ..stats.storage import BaseStorage, MemoryStorage
from ..stats import StatsManager
from ..utils.callback_data import CallbackData

U = TypeVar("U", bound=Union[Update, Message, CallbackQuery])


class Dispatcher:
    def __init__(self, bot: Bot, storage: Optional[BaseStorage] = None):
        self.bot = bot
        self.routers: List[Router] = []
        self.storage = storage or MemoryStorage()

    def include_router(self, router: "Router") -> None:
        self.routers.append(router)

    async def process(self, update: Update) -> None:
        handler, middlewares = await self._find_handler(update=update)
        if not handler:
            return

        wrapped = handler.callback
        for middleware in reversed(middlewares.middlewares):
            wrapped = self._wrap_middleware(middleware, wrapped)

        kwargs = await self._build_handler_kwargs(wrapped, update)

        await wrapped(**kwargs)

    def _wrap_middleware(self, middleware, handler: Callable) -> Callable:
        async def wrapper(update: Update, data: Dict[str, Any]) -> Any:
            return await middleware(handler, update, data)

        return wrapper

    async def _find_handler(
        self, update: Update
    ) -> Optional[Tuple[Handler, MiddlewareHandler]]:
        stats = await self.storage.get_stats(update.origin.from_user.chatid)
        for router in self.routers:
            handler = await router.matches_update(update=update, stats=stats)
            if handler:
                return (handler, router.middleware)
        return None, None

    async def _build_handler_kwargs(
        self, callback: Callable, update: Update
    ) -> dict[str, Any]:
        sig = inspect.signature(callback)
        kwargs = {}
        data = update.data
        origin = update.origin

        for name, param in sig.parameters.items():
            if name == "update":
                kwargs[name] = update
            elif name == "stats":
                kwargs[name] = StatsManager(
                    key=int(origin.from_user.chatid), storage=self.storage
                )
            elif hasattr(update, name):
                kwargs[name] = getattr(update, name)
            elif name == "callback_data" and update.callback_query:
                callback_data_type = param.annotation
                if isinstance(callback_data_type, type) and issubclass(
                    callback_data_type, CallbackData
                ):
                    kwargs[name] = callback_data_type.unpack(update.callback_query.data)
            elif name in data:
                kwargs[name] = data[name]

        return kwargs
