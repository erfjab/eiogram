from typing import Optional
from ._base import Filter
from ..stats import State


class StatsFilter(Filter):
    def __init__(self, state: Optional[State]):
        super().__init__(lambda stats: (stats is not None and stats == state.name))
