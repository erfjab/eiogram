from typing import Optional, Union
from eiogram.types import Message
from ._base import MethodBase


class EditMessageText(MethodBase):
    async def execute(
        self,
        text: str,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
    ) -> Message:
        data = {
            "text": text,
            "parse_mode": "HTML",
        }

        if inline_message_id:
            data["inline_message_id"] = inline_message_id
        else:
            data.update({"chat_id": chat_id, "message_id": message_id})

        response = await self._make_request("POST", "editMessageText", data)
        result = response["result"]
        result["bot"] = self.bot
        return Message(**result)
