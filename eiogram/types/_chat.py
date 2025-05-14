from enum import StrEnum
from dataclasses import dataclass
from typing import Optional, Union
from ._base import Validated


class ChatType(StrEnum):
    PRIVATE = "private"
    GROUP = "group"
    SUPER_GROUP = "supergroup"
    CHANNEL = "channel"


@dataclass
class Chat(Validated):
    id: int
    type: Union[ChatType, str]
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @property
    def chatid(self) -> int:
        return self.id

    @property
    def is_private(self) -> bool:
        return self.type == ChatType.PRIVATE

    @property
    def full_name(self) -> str:
        if self.title:
            return self.title

        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    def __str__(self) -> str:
        return (
            f"Chat(id={self.id}, "
            f"name={self.full_name}, "
            f"username={self.username or 'N/A'})"
        )
