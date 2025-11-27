from typing import Optional
from pydantic import Field
from ._base import BotModel
from ._user import User
from ._message import Message
from ._chat import Chat


class CallbackQuery(BotModel):
    id: str
    from_user: User = Field(..., alias="from")
    message: Optional[Message] = None
    data: Optional[str] = None

    def __str__(self) -> str:
        return f"CallbackQuery(id={self.id}, from={self.from_user.full_name}, data={self.data})"

    @property
    def chat(self) -> Optional[Chat]:
        return self.message.chat if self.message else None

    async def answer(self, text: Optional[str] = None, show_alert: Optional[bool] = None) -> bool:
        return await self.bot.answer_callback(callback_query_id=self.id, text=text, show_alert=show_alert)
