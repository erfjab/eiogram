from typing import Optional, Union
from ..types import Message, InlineKeyboardMarkup
from ._base import MethodBase


class EditMessage(MethodBase):
    async def execute(
        self,
        text: str,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        data = {
            "text": text,
        }

        if reply_markup:
            data["reply_markup"] = reply_markup.dict()

        if inline_message_id:
            data["inline_message_id"] = inline_message_id
        else:
            data.update({"chat_id": chat_id, "message_id": message_id})

        response = await self._make_request("POST", "editMessageText", data)
        message = Message.from_dict(response["result"])
        message.set_bot(self.bot)
        return message
