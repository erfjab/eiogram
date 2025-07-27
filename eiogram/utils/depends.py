from typing import TypeVar, Callable

T = TypeVar("T")


class Depends:
    def __init__(self, dependency: Callable):
        self.dependency = dependency
