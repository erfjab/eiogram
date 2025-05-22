from typing import Optional, Any, Union
from pydantic import BaseModel, root_validator
from ._message import Message
from ._callback_query import CallbackQuery
from ..client import Bot


class Update(BaseModel):
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    data: dict[str, Any] = {}
    bot: Optional[Bot] = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def origin(self) -> Optional[Union[Message, CallbackQuery]]:
        return self.message or self.callback_query

    @root_validator(pre=True)
    def inject_bot_to_submodels(cls, values):
        bot = values.get("bot")
        if bot:
            # Handle message
            if "message" in values and values["message"] is not None:
                if isinstance(values["message"], dict):
                    values["message"]["bot"] = bot
                elif isinstance(values["message"], Message):
                    values["message"].bot = bot

            # Handle callback_query
            if "callback_query" in values and values["callback_query"] is not None:
                if isinstance(values["callback_query"], dict):
                    values["callback_query"]["bot"] = bot
                    values["callback_query"]["message"]["bot"] = bot
                elif isinstance(values["callback_query"], CallbackQuery):
                    values["callback_query"].bot = bot
                    values["callback_query"]["message"].bot = bot

        return values

    def __getitem__(self, key: str) -> Any:
        """Get item from data dictionary"""
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item in data dictionary"""
        self.data[key] = value
