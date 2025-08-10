import inspect
import asyncio
import logging
from typing import Optional, TypeVar, Union, List, Tuple, Callable, Dict, Any, get_origin, get_args, Annotated
from ._handlers import Handler, MiddlewareHandler, FallbackHandler, ErrorHandler
from ._router import Router
from ..client import Bot
from ..types import Update, Message, CallbackQuery, InlineQuery
from ..state import StateManager
from ..state.storage import BaseStorage, MemoryStorage
from ..utils.callback_data import CallbackData
from ..utils.depends import Depends

U = TypeVar("U", bound=Union[Update, Message, CallbackQuery])


class Dispatcher:
    def __init__(self, bot: Bot, storage: Optional[BaseStorage] = None):
        self.bot = bot
        self.routers: List[Router] = []
        self.storage = storage or MemoryStorage()
        self.fallback = FallbackHandler()
        self.error = ErrorHandler()
        self._logger = logging.getLogger(__name__)

    def include_router(self, router: "Router") -> None:
        self.routers.append(router)

    async def process(self, update: Update) -> None:
        try:
            user_context = await self._get_user_context(update.origin.from_user.chatid)
            handler, middlewares = await self._find_handler(update, user_context["state"])
            if not handler:
                if self.fallback.handler:
                    kwargs = await self._build_handler_kwargs(
                        self.fallback.handler, update, user_data=user_context["data"], middleware_data={}
                    )
                    await self.fallback.handler(**kwargs)
                return

            final_handler = await self._build_final_handler(handler.callback, update, user_context["data"])
            wrapped_handler = self._wrap_middlewares(middlewares.middlewares, final_handler)
            await wrapped_handler(update, user_context["data"])
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

    async def _build_final_handler(self, handler: Callable, update: Update, user_data: Dict[str, Any]) -> Callable:
        async def final_handler(update: Update, data: Dict[str, Any]) -> Any:
            kwargs = await self._build_handler_kwargs(handler, update, user_data=user_data, middleware_data=data)
            return await handler(**kwargs)

        return final_handler

    async def _find_handler(self, update: Update, current_state: Optional[str]) -> Optional[Tuple[Handler, MiddlewareHandler]]:
        for router in self.routers:
            handler = await router.matches_update(update=update, state=current_state)
            if handler:
                return handler, router.middleware
        return None, None

    async def _get_user_context(self, chat_id: Union[int, str]) -> Dict[str, Any]:
        storage_data = await self.storage.get_context(int(chat_id))
        return {"state": storage_data.get("state", None), "data": storage_data.get("data", {})}

    def _get_dependency_from_annotated(self, param_type: Any) -> Optional[Depends]:
        if get_origin(param_type) is Annotated:
            for arg in get_args(param_type)[1:]:
                if isinstance(arg, Depends):
                    return arg
        return None

    async def _build_handler_kwargs(
        self, handler: Callable, update: Update, user_data: Dict[str, Any], middleware_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        sig = inspect.signature(handler)
        kwargs = {}
        origin = update.origin
        for key, value in middleware_data.items():
            if key not in kwargs and key in sig.parameters:
                kwargs[key] = value

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
            param_default = param.default

            if param_type in type_mapping:
                value = type_mapping[param_type]
                if value is not None:
                    kwargs[param_name] = value
            elif param_name == "state_data":
                kwargs[param_name] = user_data
            elif update.callback_query and inspect.isclass(param_type) and issubclass(param_type, CallbackData):
                kwargs[param_name] = param_type.unpack(update.callback_query.data)
            elif hasattr(update, param_name):
                kwargs[param_name] = getattr(update, param_name)
            elif hasattr(update, "data") and param_name in update.data:
                kwargs[param_name] = update.data[param_name]
            else:
                annotated_dependency = self._get_dependency_from_annotated(param_type)
                if annotated_dependency:
                    dependency_func = annotated_dependency.dependency
                    dep_kwargs = await self._build_handler_kwargs(dependency_func, update, user_data, middleware_data)
                    kwargs[param_name] = await dependency_func(**dep_kwargs)
                elif isinstance(param_default, Depends):
                    dependency_func = param_default.dependency
                    dep_kwargs = await self._build_handler_kwargs(dependency_func, update, user_data, middleware_data)
                    kwargs[param_name] = await dependency_func(**dep_kwargs)

        return kwargs

    async def run_polling(
        self,
        *,
        interval: float = 1.0,
        limit: int = 100,
        timeout: int = 0,
        allowed_updates: Optional[List[str]] = None,
        offset: Optional[int] = None,
    ) -> None:
        self._logger.info(f"Polling started (interval={interval}, timeout={timeout})")
        last_highest: Optional[int] = None
        pending: set[asyncio.Task] = set()

        def _task_done(t: asyncio.Task) -> None:
            pending.discard(t)
            if t.cancelled():
                return
            exc = t.exception()
            if exc:
                self._logger.exception(f"Unhandled exception in update task: {exc}")

        while True:
            try:
                try:
                    updates = await self.bot.get_updates(
                        offset=offset,
                        limit=limit,
                        timeout=timeout,
                        allowed_updates=allowed_updates,
                    )
                except Exception as e:
                    self._logger.exception(f"Error while fetching updates: {e}")
                    if timeout == 0:
                        await asyncio.sleep(interval)
                    continue

                if updates:
                    highest = max(u.update_id for u in updates)
                    if last_highest is None or highest > last_highest:
                        offset = highest + 1
                        last_highest = highest
                    for upd in updates:
                        t = asyncio.create_task(self.process(upd))
                        pending.add(t)
                        t.add_done_callback(_task_done)

                if timeout == 0:
                    await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as loop_error:
                self._logger.exception(f"Unexpected error in polling loop: {loop_error}")
                await asyncio.sleep(interval)

        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
        self._logger.info("Polling stopped")
