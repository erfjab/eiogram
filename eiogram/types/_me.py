from dataclasses import dataclass
from typing import Optional
from ._base import Validated


@dataclass
class Me(Validated):
    id: int
    is_bot: bool
    first_name: str
    username: str

    @property
    def chatid(self) -> str:
        return self.id

    @property
    def full_name(self) -> str:
        return self.first_name

    @property
    def mention(self) -> Optional[str]:
        return f"@{self.username}" if self.username else None

    def __str__(self) -> str:
        return (
            f"Bot(id={self.id}, "
            f"name={self.full_name}, "
            f"username={self.username or 'N/A'})"
        )
