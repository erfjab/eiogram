from typing import Callable, Any
from dataclasses import dataclass


@dataclass
class Filter:
    func: Callable[[Any], bool]

    def __call__(self, update: Any) -> bool:
        return self.func(update)

    def __and__(self, other):
        return Filter(lambda x: self(x) and other(x))

    def __or__(self, other):
        return Filter(lambda x: self(x) or other(x))

    def __invert__(self):
        return Filter(lambda x: not self(x))


class _BaseTextFilter(Filter):
    """Base class for filters that check text or caption"""

    def __init__(self, check_func: Callable[[str], bool], context: bool = False):
        def filter_func(msg: Any) -> bool:
            if context:
                texts = [getattr(msg, attr, None) for attr in ("text", "caption")]
                return any(t is not None and check_func(t) for t in texts)
            return hasattr(msg, "text") and check_func(msg.text)

        super().__init__(filter_func)
