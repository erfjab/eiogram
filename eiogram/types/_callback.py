from dataclasses import dataclass
from typing import Optional
from ._user import User
from ._message import Message
from ._base import Validated

from ..core._bot import Bot


@dataclass
class Callback(Validated):
    id: str
    from_user: Optional[User] = None
    message: Optional[Message] = None
    data: Optional[str] = None
    inline_message_id: Optional[str] = None

    _bot: Optional[object] = None

    @property
    def bot(self) -> Bot:
        if self._bot is None:
            raise AttributeError("Bot instance not set. Use Message.set_bot() first.")
        return self._bot

    @classmethod
    def set_bot(cls, bot_instance):
        cls._bot = bot_instance

    @property
    def is_inline(self) -> bool:
        return self.inline_message_id is not None

    def __str__(self) -> str:
        source = (
            f"inline:{self.inline_message_id}"
            if self.is_inline
            else f"msg:{self.message.id}"
        )
        return f"Callback(id={self.id}, from={self.from_user.full_name}, data={self.data}, source={source})"
