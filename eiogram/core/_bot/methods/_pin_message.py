from typing import Union, Optional
from ._base import MethodBase


class PinMessage(MethodBase):
    async def execute(
        self,
        message_id: int,
        chat_id: Union[int, str],
        disable_notification: Optional[bool] = False,
    ) -> bool:
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "disable_notification": disable_notification,
        }
        response = await self._make_request("POST", "pinChatMessage", data)
        return response.get("result", False)
