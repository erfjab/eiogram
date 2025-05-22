from typing import List, Union
from ._base import MethodBase


class DeleteMessages(MethodBase):
    async def execute(self, chat_id: Union[int, str], message_ids: List[int]) -> bool:
        data = {"chat_id": chat_id, "message_ids": message_ids}
        response = await self._make_request("POST", "deleteMessages", data)
        return response.get("result", False)
