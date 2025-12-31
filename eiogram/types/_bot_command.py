from dataclasses import dataclass
from ._base import BotModel


@dataclass
class BotCommand(BotModel):
    command: str
    description: str

    def __str__(self) -> str:
        return f"BotCommand(command={self.command}, description={self.description})"
