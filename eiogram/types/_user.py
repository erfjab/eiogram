from dataclasses import dataclass
from typing import Optional
from ._base import Validated


@dataclass
class User(Validated):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None

    @property
    def full_name(self) -> str:
        return (
            f"{self.first_name} {self.last_name}" if self.last_name else self.first_name
        )

    @property
    def chatid(self) -> int:
        return self.id

    @property
    def mention(self) -> Optional[str]:
        return f"@{self.username}" if self.username else None

    def __str__(self) -> str:
        return (
            f"User(id={self.id}, "
            f"name={self.full_name}, "
            f"username={self.username or 'N/A'})"
        )
