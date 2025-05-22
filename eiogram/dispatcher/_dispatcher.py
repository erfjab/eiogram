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
        # Find handler and its middlewares
        handler, middlewares = await self._find_handler(update=update)
        if not handler:
            return

        # Build the middleware chain
        final_handler = await self._build_final_handler(handler.callback, update)
        wrapped_handler = self._wrap_middlewares(middlewares.middlewares, final_handler)

        # Execute the entire chain
        await wrapped_handler(update, {})

    def _wrap_middlewares(
        self, 
        middlewares: List[Callable], 
        final_handler: Callable
    ) -> Callable:
        """Wrap middlewares in reverse order"""
        handler = final_handler
        for middleware in reversed(middlewares):
            handler = self._create_middleware_wrapper(middleware, handler)
        return handler

    def _create_middleware_wrapper(
        self, 
        middleware: Callable, 
        next_handler: Callable
    ) -> Callable:
        """Create a middleware wrapper"""
        async def wrapper(update: Update, data: Dict[str, Any]) -> Any:
            return await middleware(next_handler, update, data)
        return wrapper

    async def _build_final_handler(
        self, 
        handler: Callable, 
        update: Update
    ) -> Callable:
        """Create the final handler that will be called after all middlewares"""
        async def final_handler(update: Update, data: Dict[str, Any]) -> Any:
            kwargs = await self._build_handler_kwargs(handler, update, data)
            return await handler(**kwargs)
        return final_handler

    async def _find_handler(
        self, update: Update
    ) -> Optional[Tuple[Handler, MiddlewareHandler]]:
        stats = await self.storage.get_stats(update.origin.from_user.chatid)
        for router in self.routers:
            handler = await router.matches_update(update=update, stats=stats)
            if handler:
                return handler, router.middleware
        return None, None

    async def _build_handler_kwargs(
        self, 
        handler: Callable, 
        update: Update, 
        middleware_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build kwargs for the handler combining middleware data and update"""
        sig = inspect.signature(handler)
        kwargs = {**middleware_data}
        origin = update.origin

        # Add common parameters
        common_params = {
            'update': update,
            'stats': StatsManager(key=int(origin.from_user.chatid), storage=self.storage),
            'bot': self.bot,
            'message': update.message,
            'callback_query': update.callback_query,
        }

        for name, value in common_params.items():
            if name in sig.parameters and value is not None:
                kwargs[name] = value

        # Handle callback_data if needed
        if (update.callback_query and 
            'callback_data' in sig.parameters and 
            inspect.isclass(sig.parameters['callback_data'].annotation) and
            issubclass(sig.parameters['callback_data'].annotation, CallbackData)):
            
            kwargs['callback_data'] = sig.parameters['callback_data'].annotation.unpack(
                update.callback_query.data
            )

        # Add any additional parameters
        for param in sig.parameters:
            if param not in kwargs:
                if hasattr(update, param):
                    kwargs[param] = getattr(update, param)
                elif param in update.data:
                    kwargs[param] = update.data[param]

        return kwargs