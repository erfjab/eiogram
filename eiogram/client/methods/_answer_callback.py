from typing import Optional
from ._base import MethodBase


class AnswerCallbackQuery(MethodBase):
    async def execute(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
    ) -> bool:
        data = {
            "callback_query_id": callback_query_id,
        }

        if text:
            data["text"] = text

        if show_alert is not None:
            data["show_alert"] = show_alert

        response = await self._make_request("POST", "answerCallbackQuery", data)
        return response.get("result", False)
