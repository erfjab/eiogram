from typing import Optional, Union
from ...types import Message
from ._base import MethodBase


class ForwardMessage(MethodBase):
    async def execute(
        self,
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_id: int,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = None,
    ) -> Optional[Message]:
        data = {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
        }

        if disable_notification is not None:
            data["disable_notification"] = disable_notification

        if protect_content is not None:
            data["protect_content"] = protect_content

        response = await self._make_request("POST", "forwardMessage", data)
        result = response["result"]
        result["bot"] = self.bot
        return Message(**result)
