from typing import Optional, Any, Union
from pydantic import BaseModel
from ._message import Message
from ._callback_query import CallbackQuery


class Update(BaseModel):
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    data: dict[str, Any] = {}

    @property
    def origin(self) -> Optional[Union[Message, CallbackQuery]]:
        return self.message or self.callback_query

    def __getitem__(self, key: str) -> Any:
        """Get item from data dictionary"""
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item in data dictionary"""
        self.data[key] = value
