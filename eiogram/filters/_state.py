from typing import Optional
from ._base import Filter
from ..state import State


class StateFilter(Filter):
    def __init__(self, state: Optional[State]):
        super().__init__(lambda state: (state is not None and state == state.name))


class IgnoreStateFilter(Filter):
    def __init__(self):
        super().__init__(lambda x: True)
