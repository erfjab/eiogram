import inspect
from typing import Optional, TypeVar, Union, List, Tuple, Callable, Dict, Any
from ._handlers import Handler, MiddlewareHandler
from ._router import Router
from ..client import Bot
from ..types import Update, Message, CallbackQuery, InlineQuery
from ..state.storage import BaseStorage, MemoryStorage
from ..state import StateManager
from ..utils.callback_data import CallbackData
from ._handlers import FallbackHandler, ErrorHandler

U = TypeVar("U", bound=Union[Update, Message, CallbackQuery])


class Dispatcher:
    def __init__(self, bot: Bot, storage: Optional[BaseStorage] = None):
        self.bot = bot
        self.routers: List[Router] = []
        self.storage = storage or MemoryStorage()
        self.fallback = FallbackHandler()
        self.error = ErrorHandler()

    def include_router(self, router: "Router") -> None:
        self.routers.append(router)

    async def process(self, update: Update) -> None:
        try:
            handler, middlewares = await self._find_handler(update=update)
            if not handler:
                if self.fallback.handler:
                    kwargs = await self._build_handler_kwargs(self.fallback.handler, update, {})
                    await self.fallback.handler(**kwargs)
                return

            final_handler = await self._build_final_handler(handler.callback, update)
            wrapped_handler = self._wrap_middlewares(middlewares.middlewares, final_handler)

            await wrapped_handler(update, {})

        except Exception as e:
            await self._handle_error(e, update)

    async def _handle_error(self, error: Exception, update: Update) -> None:
        for exception_type, handler in self.error.handlers:
            if exception_type is not None and isinstance(error, exception_type):
                await handler(error, update)
                return

        for exception_type, handler in self.error.handlers:
            if exception_type is None:
                await handler(error, update)
                return

        raise error

    def _wrap_middlewares(self, middlewares: List[Callable], final_handler: Callable) -> Callable:
        handler = final_handler
        for middleware in reversed(middlewares):
            handler = self._create_middleware_wrapper(middleware, handler)
        return handler

    def _create_middleware_wrapper(self, middleware: Callable, next_handler: Callable) -> Callable:
        async def wrapper(update: Update, data: Dict[str, Any]) -> Any:
            return await middleware(next_handler, update, data)

        return wrapper

    async def _build_final_handler(self, handler: Callable, update: Update) -> Callable:
        async def final_handler(update: Update, data: Dict[str, Any]) -> Any:
            kwargs = await self._build_handler_kwargs(handler, update, data)
            return await handler(**kwargs)

        return final_handler

    async def _find_handler(self, update: Update) -> Optional[Tuple[Handler, MiddlewareHandler]]:
        state = await self.storage.get_state(update.origin.from_user.chatid)
        for router in self.routers:
            handler = await router.matches_update(update=update, state=state)
            if handler:
                return handler, router.middleware
        return None, None

    async def _build_handler_kwargs(self, handler: Callable, update: Update, middleware_data: Dict[str, Any]) -> Dict[str, Any]:
        sig = inspect.signature(handler)
        kwargs = {}
        origin = update.origin
        for name, value in middleware_data.items():
            if name in sig.parameters:
                kwargs[name] = value
        type_mapping = {
            Update: update,
            StateManager: StateManager(key=int(origin.from_user.chatid), storage=self.storage),
            Bot: self.bot,
            Message: update.message,
            CallbackQuery: update.callback_query,
            InlineQuery: update.inline_query,
        }

        for param_name, param in sig.parameters.items():
            if param_name in kwargs:
                continue

            param_type = param.annotation

            if param_type in type_mapping:
                value = type_mapping[param_type]
                if value is not None:
                    kwargs[param_name] = value

            elif update.callback_query and inspect.isclass(param_type) and issubclass(param_type, CallbackData):
                kwargs[param_name] = param_type.unpack(update.callback_query.data)

            elif hasattr(update, param_name):
                kwargs[param_name] = getattr(update, param_name)
            elif hasattr(update, "data") and param_name in update.data:
                kwargs[param_name] = update.data[param_name]

        return kwargs
