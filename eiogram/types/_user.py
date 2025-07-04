from typing import Optional, Union
from pydantic import BaseModel
from ..client import Bot


class User(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    bot: Optional[Bot] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}" if self.last_name else self.first_name

    @property
    def chatid(self) -> int:
        return self.id

    @property
    def mention(self) -> Optional[str]:
        return f"@{self.username}" if self.username else None

    def __str__(self) -> str:
        return f"User(id={self.id}, name={self.full_name}, username={self.username or 'N/A'})"

    async def is_join(
        self,
        chat_id: Union[str, int],
    ) -> bool:
        from ._chat import ChatMemberStatus

        try:
            status = await self.bot.get_chat_member(chat_id=chat_id, user_id=self.id)
            if status and status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR,
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.RESTRICTED,
            ]:
                return True
        except Exception:
            return False

    async def is_admin(
        self,
        chat_id: Union[str, int],
    ) -> bool:
        from ._chat import ChatMemberStatus

        try:
            status = await self.bot.get_chat_member(chat_id=chat_id, user_id=self.id)
            if status and status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR,
            ]:
                return True
        except Exception:
            return False
