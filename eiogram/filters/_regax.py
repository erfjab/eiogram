import re
from typing import Union, Pattern
from ._base import BaseTextFilter


class Regex(BaseTextFilter):
    """Filter text/caption matching regex pattern"""

    def __init__(self, pattern: Union[str, Pattern], check_context: bool = False):
        compiled = re.compile(pattern)
        super().__init__(lambda t: bool(compiled.search(t)), check_context)
