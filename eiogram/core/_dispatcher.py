from typing import (
    Any,
    Dict,
    List,
    Optional,
    TypeVar,
    Union,
    Callable,
    Awaitable,
    TYPE_CHECKING,
)
import inspect
from ._handlers import Handler, ErrorHandler, FilterFunc
from ..types import Update, Message, CallbackQuery
from ..stats import BaseStorage, MemoryStorage, StatsData
from .middlewares import BaseMiddleware

if TYPE_CHECKING:
    from ._router import Router

U = TypeVar("U", bound=Union[Update, Message, CallbackQuery])


class Dispatcher:
    def __init__(self, bot: Any, storage: Optional[BaseStorage] = None):
        self.bot = bot
        self.handlers: Dict[str, List[Handler]] = {
            "message": [],
            "callback_query": [],
        }
        self.middlewares: List[BaseMiddleware] = []
        self.error = ErrorHandler()
        self.routers: List["Router"] = []
        self.storage = storage or MemoryStorage()

    def include_router(self, router: "Router") -> None:
        self.routers.append(router)
        router.setup(self)

    async def _process_middlewares(
        self, update: U, handler: Callable[[U, Dict[str, Any]], Awaitable[Any]]
    ) -> Any:
        data: Dict[str, Any] = {}
        final_handler = handler

        for middleware in reversed(self.middlewares):
            final_handler = self._wrap_middleware(middleware, final_handler)

        return await final_handler(update, data)

    def _wrap_middleware(
        self,
        middleware: BaseMiddleware,
        handler: Callable[[U, Dict[str, Any]], Awaitable[Any]],
    ) -> Callable[[U, Dict[str, Any]], Awaitable[Any]]:
        async def wrapper(update: U, data: Dict[str, Any]) -> Any:
            return await middleware(handler, update, data)

        return wrapper

    def register(
        self,
        update_type: str,
        handler: Callable[[U], Awaitable[None]],
        filters: Optional[List[FilterFunc]] = None,
        priority: int = 0,
    ) -> None:
        if update_type not in self.handlers:
            raise ValueError(f"Invalid update type: {update_type}")

        self.handlers[update_type].append(Handler(handler, filters or [], priority))
        self.handlers[update_type].sort(key=lambda x: x.priority, reverse=True)

    async def process(self, update: Update) -> None:
        update.bot = self.bot
        handler = await self._find_handler(update)
        if not handler:
            raise ValueError("No matching handler found for update")

        async def handler_wrapper(update: U, data: Dict[str, Any]) -> None:
            await self._run_handler(handler.callback, update, data)

        await self._process_middlewares(update, handler_wrapper)

    async def _find_handler(self, update: Update) -> Optional[Handler]:
        for router in self.routers:
            handler = await router.matches_update(update)
            if handler:
                return handler
        return None

    async def _run_handler(
        self, callback: Callable, update: Update, data: Optional[Dict[str, Any]] = None
    ) -> None:
        if data is None:
            data = {}

        sig = inspect.signature(callback)
        kwargs: Dict[str, Any] = {}

        # Add common parameters
        if "bot" in sig.parameters:
            kwargs["bot"] = self.bot
        if "message" in sig.parameters and update.message:
            kwargs["message"] = update.message
        if "callback_query" in sig.parameters and update.callback:
            kwargs["callback_query"] = update.callback
            callback_data = sig.parameters.get("callback_data", None)
            if callback_data:
                kwargs["callback_data"] = callback_data.annotation.unpack(
                    update.callback_query.data
                )
        if "stats" in sig.parameters:
            kwargs["stats"] = StatsData(
                key=int(update.origin.from_user.chatid), storage=self.storage
            )

        # Add data and update parameters
        for param in sig.parameters:
            if param in data:
                kwargs[param] = data[param]
            elif hasattr(update, param):
                kwargs[param] = getattr(update, param)

        await callback(**kwargs)
