from typing import Optional
from enum import StrEnum
from pydantic import BaseModel


class ChatType(StrEnum):
    PRIVATE = "private"
    GROUP = "group"
    SUPER_GROUP = "supergroup"
    CHANNEL = "channel"


class ChatMemberStatus(StrEnum):
    CREATOR = "creator"
    ADMINISTRATOR = "administrator"
    MEMBER = "member"
    RESTRICTED = "restricted"
    LEFT = "left"
    KICKED = "kicked"


class Chat(BaseModel):
    id: int
    type: ChatType
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

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
            f"Chat(id={self.id}, "
            f"name={self.full_name}, "
            f"username={self.username or 'N/A'}, "
            f"type={self.type})"
        )
