from pydantic import BaseModel


class BotCommand(BaseModel):
    command: str
    description: str

    def __str__(self) -> str:
        return f"BotCommand(command={self.command}, description={self.description})"
