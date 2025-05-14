from dataclasses import dataclass
from typing import Callable, Awaitable, Optional, TypeVar, List
from functools import wraps

from ...types import Update

U = TypeVar("U", bound=Update)
MiddlewareFunc = Callable[[U], Awaitable[Optional[U]]]


@dataclass
class Middleware:
    func: MiddlewareFunc
    priority: int = 0


class MiddlewareHandler:
    def __init__(self):
        self.middlewares: List[Middleware] = []

    def __call__(self, priority: int = 0) -> Callable[[MiddlewareFunc], MiddlewareFunc]:
        def decorator(func: MiddlewareFunc) -> MiddlewareFunc:
            @wraps(func)
            async def wrapper(update: U) -> Optional[U]:
                return await func(update)

            self.middlewares.append(Middleware(wrapper, priority))
            self.middlewares.sort(key=lambda m: m.priority, reverse=True)
            return func

        return decorator
