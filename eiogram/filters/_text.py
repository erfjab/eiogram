from typing import Optional
from ._base import BaseTextFilter


class Text(BaseTextFilter):
    """Filter text/caption matching exactly"""

    def __init__(self, text: Optional[str] = None, check_context: bool = False):
        if text is None:
            super().__init__(lambda _: True, check_context)
        else:
            super().__init__(lambda t: t == text, check_context)
