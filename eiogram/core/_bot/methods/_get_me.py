from typing import Optional
from eiogram.types._me import Me
from ._base import MethodBase


class GetMe(MethodBase):
    async def execute(self) -> Optional[Me]:
        response = await self._make_request("GET", "getMe")
        return Me.from_dict(response["result"]) if response.get("result") else None
