from typing import Optional
from ._base import MethodBase


class DeleteWebhook(MethodBase):
    async def execute(self, drop_pending_updates: Optional[bool] = False) -> bool:
        params = {"drop_pending_updates": drop_pending_updates}
        response = await self._make_request("GET", "deleteWebhook", params=params)
        return response.get("result", False)
