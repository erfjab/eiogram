from typing import Optional, List
from ._base import MethodBase


class SetWebhook(MethodBase):
    async def execute(
        self,
        url: str,
        max_connections: int = 40,
        allowed_updates: Optional[List[str]] = None,
        drop_pending_updates: bool = False,
        secret_token: Optional[str] = None,
    ) -> bool:
        data = {
            "url": url,
            "max_connections": max_connections,
            "drop_pending_updates": drop_pending_updates,
        }

        if allowed_updates:
            data["allowed_updates"] = allowed_updates

        if secret_token:
            data["secret_token"] = secret_token

        response = await self._make_request("POST", "setWebhook", data)
        return response.get("result", False)
