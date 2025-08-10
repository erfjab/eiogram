from typing import Optional, List, TYPE_CHECKING, Any, Dict
from ._base import MethodBase

if TYPE_CHECKING:
    from ...types import Update


class GetUpdates(MethodBase):
    async def execute(
        self,
        offset: Optional[int] = None,
        limit: int = 100,
        timeout: int = 0,
        allowed_updates: Optional[List[str]] = None,
    ) -> List["Update"]:
        from ...types import Update

        data: Dict[str, Any] = {"limit": limit, "timeout": timeout}
        if offset is not None:
            data["offset"] = offset
        if allowed_updates is not None:
            data["allowed_updates"] = allowed_updates

        response = await self._make_request("POST", "getUpdates", params=data)
        result = response.get("result", [])
        updates: List[Update] = []
        for raw in result:
            raw["bot"] = self.bot
            updates.append(Update(**raw))
        return updates
