from functools import partial
from ._base import BaseTextFilter


class Command(BaseTextFilter):
    """Filter commands in text/caption"""

    def __init__(self, command: str = "start", check_context: bool = False):
        cmd = command.lower().strip("/")
        super().__init__(lambda t: t.lower().startswith(f"/{cmd}"), check_context)


StartCommand = partial(Command, command="start")
HelpCommand = partial(Command, command="help")
VersionCommand = partial(Command, command="version")
