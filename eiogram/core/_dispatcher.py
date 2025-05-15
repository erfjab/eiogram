from typing import (
    Any,
    Dict,
    List,
    Optional,
    TypeVar,
    Union,
    Callable,
    TYPE_CHECKING,
    Awaitable,
)
import inspect

from .handlers import Handler, Middleware, ErrorHandler, FilterFunc
from ..types import Update, Message, Callback
from ..utils._stats import BaseStorage, MemoryStorage, StatsData

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
        self.middlewares: List[Middleware] = []
        self.error = ErrorHandler()
        self.routers: List["Router"] = []
        self.storage = storage

    def include_router(self, router: "Router") -> None:
        self.routers.append(router)
        router.setup(self)

    async def _process_middlewares(self, update: U) -> Optional[U]:
        current_data = update
        for mw in self.middlewares:
            try:
                current_data = await mw.func(current_data)
                if current_data is None:
                    return None
            except Exception as e:
                if not await self.error.handle(e):
                    raise
        return current_data

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

            processed_update = await self._process_middlewares(update)
            if processed_update is None:
                return

            for router in self.routers:
                handler = await router.matches_update(processed_update)
                if not handler:
                    continue

                try:
                    await self._run_handler(handler.callback, processed_update)
                    return
                except Exception as e:
                    if not await self.error.handle(e):
                        raise

        except Exception as e:
            if not await self.error.handle(e):
                raise

    async def _run_handler(self, callback: Callable, update: Update):
        sig = inspect.signature(callback)
        kwargs = {}

        if "bot" in sig.parameters and self.bot:
            kwargs["bot"] = self.bot

        if "message" in sig.parameters and update.message:
            kwargs["message"] = update.message
            if self.bot:
                update.message.set_bot(self.bot)
        elif "callback" in sig.parameters and update.callback:
            kwargs["callback"] = update.callback
            if self.bot:
                update.callback.set_bot(self.bot)

        if "stats" in sig.parameters:
            kwargs["stats"] = StatsData(
                key=int(update.origin.from_user.chatid), storage=self.storage
            )

        await callback(**kwargs)
