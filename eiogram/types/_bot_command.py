from dataclasses import dataclass
from ._base import Validated


@dataclass
class BotCommand(Validated):
    command: str
    description: str

    def dict(self) -> dict:
        return {"command": self.command, "description": self.description}

    def __str__(self) -> str:
        return f"BotCommand(command={self.command}, description={self.description})"
