from typing import Callable, Awaitable, List, Optional, Type, TypeVar

E = TypeVar("E", bound=Exception)
ErrorHandlerFunc = Callable[[E], Awaitable[Optional[bool]]]


class ErrorHandler:
    def __init__(self):
        self.handlers: List[tuple[Optional[Type[Exception]], ErrorHandlerFunc]] = []

    def __call__(self, exception_type: Optional[Type[Exception]] = None):
        def decorator(func: ErrorHandlerFunc) -> ErrorHandlerFunc:
            self.handlers.append((exception_type, func))
            return func

        return decorator
