from typing import Optional
from ._base import Filter
from ..state import State


class StateFilter(Filter):
    def __init__(self, state: Optional[State]):
        super().__init__(lambda s: (s is not None and s == state.name))


class IgnoreStateFilter(Filter):
    def __init__(self):
        super().__init__(lambda _: True)
