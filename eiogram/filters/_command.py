from functools import partial
from ._base import _BaseTextFilter


class Command(_BaseTextFilter):
    """Simple command filter with exact argument count"""

    def __init__(
        self,
        command: str,
        *,
        args_count: int = 0,
        prefix: str = "/",
        context: bool = False,
    ):
        cmd = command.lower().strip(prefix)

        def check_func(text: str) -> bool:
            text = text.lower().strip()
            parts = text.split()
            return len(parts) == args_count + 1 and parts[0] == f"{prefix}{cmd}"

        super().__init__(check_func, context)


StartCommand = partial(Command, command="start")
VersionCommand = partial(Command, command="version")
