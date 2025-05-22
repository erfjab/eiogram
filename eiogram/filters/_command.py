from functools import partial
from ._base import _BaseTextFilter


class Command(_BaseTextFilter):
    """Filter commands in text/caption"""

    def __init__(self, command: str = "start", context: bool = False):
        cmd = command.lower().strip("/")
        super().__init__(lambda t: t.lower().startswith(f"/{cmd}"), context)


StartCommand = partial(Command, command="start")
VersionCommand = partial(Command, command="version")
