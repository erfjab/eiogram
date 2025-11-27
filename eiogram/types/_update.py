from typing import Optional, Any, Union
from ._base import BotModel
from ._message import Message
from ._callback_query import CallbackQuery
from ._inline_query import InlineQuery


class Update(BotModel):
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    inline_query: Optional[InlineQuery] = None
    data: dict[str, Any] = {}

    @property
    def origin(self) -> Optional[Union[Message, CallbackQuery, InlineQuery]]:
        if self.message:
            return self.message
        if self.callback_query:
            return self.callback_query
        if self.inline_query:
            return self.inline_query
        return None

    def __getitem__(self, key: str) -> Any:
        """Get item from data dictionary"""
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item in data dictionary"""
        self.data[key] = value
