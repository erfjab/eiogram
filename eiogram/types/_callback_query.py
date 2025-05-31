from typing import Optional
from pydantic import BaseModel, Field
from ._user import User
from ._message import Message
from ._chat import Chat
from ..client import Bot


class CallbackQuery(BaseModel):
    id: str
    from_user: User = Field(..., alias="from")
    message: Optional[Message] = None
    data: Optional[str] = None
    bot: Optional[Bot] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True

    def __str__(self) -> str:
        return f"CallbackQuery(id={self.id}, from={self.from_user.full_name}, data={self.data})"

    @property
    def chat(self) -> Optional[Chat]:
        return self.message.chat if self.message else None

    def answer(
        self, text: Optional[str] = None, show_alert: Optional[bool] = None
    ) -> bool:
        return self.bot.answer_callback(
            callback_query_id=self.id, text=text, show_alert=show_alert
        )
