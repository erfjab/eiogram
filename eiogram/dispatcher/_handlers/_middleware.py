from typing import List
from ...middleware import BaseMiddleware


class MiddlewareHandler:
    def __init__(self):
        self.middlewares: List[BaseMiddleware] = []

    def register(self, middleware: BaseMiddleware) -> BaseMiddleware:
        self.middlewares.append(middleware)
        self.middlewares.sort(key=lambda m: m.priority, reverse=True)
        return middleware
