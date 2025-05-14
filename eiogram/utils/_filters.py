import re
from typing import Callable, Optional, Any, Union, Pattern
from dataclasses import dataclass
from ._stats._stats import State


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


class Data(Filter):
    def __init__(self, data: str):
        self.func = lambda cb: (
            hasattr(cb, "data") and getattr(cb, "data", None) == data
        )


class Text(Filter):
    def __init__(self, text: Optional[str] = None):
        if text:
            self.func = lambda msg: (hasattr(msg, "text") and msg.text == text)
        else:
            self.func = lambda msg: hasattr(msg, "text")


class Photo(Filter):
    def __init__(self):
        self.func = lambda msg: (
            hasattr(msg, "photo") and msg.photo is not None and bool(msg.photo)
        )


class StatsFilter(Filter):
    def __init__(self, state: State):
        super().__init__(self.check)
        self.state = state

    def check(self, stats: Optional[Union[str, State]]) -> bool:
        if stats is None:
            return False
        return stats == self.state.name


class Command(Filter):
    def __init__(self, command: str):
        self.func = lambda msg: any(
            getattr(msg, attr, "").lower().startswith(f"/{command.lower()}")
            for attr in ("text", "caption")
            if isinstance(getattr(msg, attr, None), str)
        )


class And(Filter):
    def __init__(self, *filters: Filter):
        self.func = lambda x: all(f(x) for f in filters)


class Or(Filter):
    def __init__(self, *filters: Filter):
        self.func = lambda x: any(f(x) for f in filters)


class Not(Filter):
    def __init__(self, filter: Filter):
        self.func = lambda x: not filter(x)


class Regex(Filter):
    def __init__(self, pattern: Union[str, Pattern]):
        self.pattern = re.compile(pattern)
        self.func = lambda msg: (
            hasattr(msg, "text")
            and isinstance(msg.text, str)
            and bool(self.pattern.search(msg.text))
        )


class IsPrivate(Filter):
    def __init__(self):
        self.func = lambda msg: (
            hasattr(msg, "chat")
            and hasattr(msg.chat, "type")
            and msg.chat.type == "private"
        )


class IsGroup(Filter):
    def __init__(self):
        self.func = lambda msg: (
            hasattr(msg, "chat")
            and hasattr(msg.chat, "type")
            and msg.chat.type == "group"
        )


class IsSuperGroup(Filter):
    def __init__(self):
        self.func = lambda msg: (
            hasattr(msg, "chat")
            and hasattr(msg.chat, "type")
            and msg.chat.type == "supergroup"
        )


class IsChannel(Filter):
    def __init__(self):
        self.func = lambda msg: (
            hasattr(msg, "chat")
            and hasattr(msg.chat, "type")
            and msg.chat.type == "channel"
        )


class IsForum(Filter):
    def __init__(self):
        self.func = lambda msg: (
            hasattr(msg, "chat")
            and hasattr(msg.chat, "type")
            and msg.chat.type == "forum"
        )
