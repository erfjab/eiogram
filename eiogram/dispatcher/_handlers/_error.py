from typing import Callable, Awaitable, List, Type, TypeVar, Any, Tuple

E = TypeVar("E", bound=Exception)
ErrorHandlerFunc = Callable[[Any], Awaitable[None]]


class ErrorHandler:
    def __init__(self):
        self.handlers: List[Tuple[Tuple[Type[Exception], ...], ErrorHandlerFunc]] = []

    def __call__(self, *exception_types: Type[Exception]):
        def decorator(func: ErrorHandlerFunc) -> ErrorHandlerFunc:
            if not exception_types:
                self.handlers.append(((), func))
            else:
                self.handlers.append((exception_types, func))
            return func

        return decorator
