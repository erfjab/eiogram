from typing import List, Dict, Any
from ...types import BotCommand
from ._base import MethodBase


class SetMyCommands(MethodBase):
    async def execute(
        self,
        commands: List[BotCommand],
    ) -> bool:
        data: Dict[str, Any] = {"commands": [cmd.dict() for cmd in commands]}

        response = await self._make_request("POST", "setMyCommands", data)
        return response.get("result", False)
