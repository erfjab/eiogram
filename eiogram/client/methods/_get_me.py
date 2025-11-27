from typing import Optional
from ...types import User
from ._base import MethodBase


class GetMe(MethodBase):
    async def execute(self) -> Optional[User]:
        response = await self._make_request("GET", "getMe")
        result = response["result"]
        result["bot"] = self.bot
        return User(**result)
