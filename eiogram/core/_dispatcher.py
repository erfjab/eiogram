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
from .handlers import Handler, ErrorHandler, FilterFunc
from ..types import Update, Message, Callback
from ..utils._stats import BaseStorage, MemoryStorage, StatsData
from .middlewares import BaseMiddleware

if TYPE_CHECKING:
    from ._router import Router

U = TypeVar("U", bound=Union[Update, Message, Callback])


class Dispatcher:
    def __init__(self, bot: Any, storage: BaseStorage = MemoryStorage()):
        self.bot = bot
        self.handlers: Dict[str, List[Handler]] = {
            "message": [],
            "callback": [],
        }
        self.middlewares: List[BaseMiddleware] = []
        self.error = ErrorHandler()
        self.routers: List["Router"] = []
        self.storage = storage

    def include_router(self, router: "Router") -> None:
        self.routers.append(router)
        router.setup(self)

    async def _process_middlewares(
        self, update: U, handler: Callable[[U, Dict[str, Any]], Awaitable[Any]]
    ) -> Optional[Any]:
        data: Dict[str, Any] = {}

        final_handler = handler

        for middleware in reversed(self.middlewares):
            final_handler = self._wrap_middleware(middleware, final_handler)

        try:
            return await final_handler(update, data)
        except Exception as e:
            if not await self.error.handle(e):
                raise
            return None

    def _wrap_middleware(
        self,
        middleware: "BaseMiddleware",
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

        handler_entry = Handler(
            callback=handler, filters=filters or [], priority=priority
        )
        self.handlers[update_type].append(handler_entry)
        self.handlers[update_type].sort(key=lambda x: x.priority, reverse=True)

    async def process(self, update: Update) -> None:
        try:
            if update.message:
                update.message.set_bot(self.bot)
            if update.callback:
                update.callback.set_bot(self.bot)

            # Find matching handler
            handler = None
            for router in self.routers:
                handler = await router.matches_update(update)
                if handler:
                    break

            if not handler:
                return

            # Create handler wrapper
            async def handler_wrapper(update: U, data: Dict[str, Any]) -> None:
                await self._run_handler(handler.callback, update, data)

            # Process middlewares
            await self._process_middlewares(update, handler_wrapper)

        except Exception as e:
            if not await self.error.handle(e):
                raise

    async def _run_handler(
        self, callback: Callable, update: Update, data: Optional[Dict[str, Any]] = None
    ) -> None:
        if data is None:
            data = {}

        sig = inspect.signature(callback)
        kwargs: Dict[str, Any] = {}

        # Add bot if needed
        if "bot" in sig.parameters and self.bot:
            kwargs["bot"] = self.bot

        # Add message or callback if needed
        if "message" in sig.parameters and update.message:
            kwargs["message"] = update.message
        elif "callback" in sig.parameters and update.callback:
            kwargs["callback"] = update.callback

        # Add stats if needed
        if "stats" in sig.parameters:
            kwargs["stats"] = StatsData(
                key=int(update.origin.from_user.chatid), storage=self.storage
            )

        # Add data parameters
        for param in sig.parameters:
            if param in data:
                kwargs[param] = data[param]
            elif param in update.data:
                kwargs[param] = update.data[param]

        await callback(**kwargs)
