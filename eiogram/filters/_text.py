from typing import Optional
from ._base import _BaseTextFilter


class Text(_BaseTextFilter):
    """Filter text/caption matching exactly"""

    def __init__(self, text: Optional[str] = None, context: bool = False):
        if text is None:
            super().__init__(lambda _: True, context)
        else:
            super().__init__(lambda t: t == text, context)
