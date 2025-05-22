from dataclasses import dataclass, field
from typing import Optional, Union
from ._message import Message
from ._callback_query import CallbackQuery
from ._base import Validated


@dataclass
class Update(Validated):
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    data: dict = field(default_factory=dict)

    @property
    def type(self) -> Optional[str]:
        if self.message:
            return "message"
        if self.callback_query:
            return "callback_query"
        return None

    @property
    def origin(self) -> Union["Message", "CallbackQuery", None]:
        return self.message or self.callback_query

    def __getitem__(self, key: str):
        return self.data.get(key)

    def __setitem__(self, key: str, value):
        self.data[key] = value

    def __str__(self) -> str:
        return f"Update(id={self.update_id}, type={self.type})"
