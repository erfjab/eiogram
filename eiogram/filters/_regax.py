import re
from typing import Union, Pattern
from ._base import _BaseTextFilter


class Regex(_BaseTextFilter):
    """Filter text/caption matching regex pattern"""

    def __init__(self, pattern: Union[str, Pattern], context: bool = False):
        compiled = re.compile(pattern)
        super().__init__(lambda t: bool(compiled.search(t)), context)
