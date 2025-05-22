from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel
from ._user import User
from ._message import Message

if TYPE_CHECKING:
    from ..client import Bot


class CallbackQuery(BaseModel):
    id: str
    from_user: Optional[User] = None
    message: Optional[Message] = None
    data: Optional[str] = None
    bot: Bot

    def __str__(self) -> str:
        return f"CallbackQuery(id={self.id}, from={self.from_user.full_name}, data={self.data})"

    def answer(
        self, text: Optional[str] = None, show_alert: Optional[bool] = None
    ) -> bool:
        return self.bot.answer_callback(
            callback_query_id=self.id, text=text, show_alert=show_alert
        )
