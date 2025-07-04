from ._base import MethodBase
from ...types import AnswerInlineQuery
import json


class AnswerInlineQueryMethod(MethodBase):
    async def execute(self, answer: AnswerInlineQuery) -> bool:
        serialized_results = []
        for result in answer.results:
            result_dict = result.dict(by_alias=True, exclude_none=True)

            if hasattr(result, "input_message_content") and result.input_message_content:
                result_dict["input_message_content"] = result.input_message_content.dict(exclude_none=True)

            serialized_results.append(result_dict)

        data = {
            "inline_query_id": answer.inline_query_id,
            "results": json.dumps(serialized_results),
            "cache_time": answer.cache_time,
        }
        response = await self._make_request("POST", "answerInlineQuery", data)
        return response.get("result", False)
