from typing import Union, Optional
from ..types import Message, InlineKeyboardMarkup
from ._base import MethodBase


class SendPhoto(MethodBase):
    async def execute(
        self,
        chat_id: Union[int, str],
        photo: Union[str, bytes],
        caption: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        data = {
            "chat_id": chat_id,
            "photo": photo,
        }

        if caption:
            data["caption"] = caption
        if reply_markup:
            data["reply_markup"] = reply_markup.dict()

        response = await self._make_request("POST", "sendPhoto", data)
        message = Message.from_dict(response["result"])
        message.set_bot(self.bot)
        return message
