from typing import Optional, Union
from ._base import MethodBase
from ...types import ChatMemberStatus


class GetChatMember(MethodBase):
    async def execute(self, chat_id: Union[str, int], user_id: int) -> Optional[dict]:
        params = {"chat_id": chat_id, "user_id": user_id}
        response = await self._make_request("GET", "getChatMember", params=params)
        return ChatMemberStatus(response["result"]["status"])
