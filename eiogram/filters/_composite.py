from typing import Union, Iterable
from collections.abc import Sequence
from ._base import Filter


def _flatten_filters(filters: Union[Filter, Iterable[Filter]]) -> list[Filter]:
    """Flatten nested filters into a single list."""
    if isinstance(filters, Filter):
        return [filters]
    return [f for sublist in filters for f in _flatten_filters(sublist)]


class And(Filter):
    def __init__(self, *filters: Union[Filter, Sequence[Filter]]):
        flattened = _flatten_filters(filters)
        super().__init__(lambda x: all(f(x) for f in flattened))


class Or(Filter):
    def __init__(self, *filters: Union[Filter, Sequence[Filter]]):
        flattened = _flatten_filters(filters)
        super().__init__(lambda x: any(f(x) for f in flattened))


class Not(Filter):
    def __init__(self, filter: Filter):
        super().__init__(lambda x: not filter(x))
