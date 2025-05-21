from typing import Union
from ._base import MethodBase


class RestrictUser(MethodBase):
    async def execute(
        self,
        chat_id: Union[int, str],
        user_id: int,
        until_date: int,
    ) -> bool:
        data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "until_date": until_date,
            "permissions": {"can_send_messages": False},
        }

        response = await self._make_request("POST", "restrictChatMember", data)
        return response.get("result", False)
