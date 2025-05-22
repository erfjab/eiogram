from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Any
from ._message import Message
from ._callback_query import CallbackQuery
from ._base import Validated
from ..core._bot import Bot


@dataclass
class Update(Validated):
    update_id: int
    message: Optional[Message] = None
    callback_query: Optional[CallbackQuery] = None
    data: Dict[str, Any] = field(default_factory=dict)
    _bot: Optional[Bot] = field(default=None, repr=False)

    @property
    def bot(self) -> Bot:
        """Get the bot instance associated with this update"""
        if self._bot is None:
            raise AttributeError("Bot instance not set for this update")
        return self._bot

    @bot.setter
    def bot(self, bot_instance: Bot) -> None:
        """Set the bot instance and automatically propagate it to all nested objects"""
        self._bot = bot_instance
        self._propagate_bot()

    def _propagate_bot(self) -> None:
        """Propagate the bot instance to all nested objects"""
        if self.message:
            self.message._bot = self._bot
        if self.callback_query:
            self.callback_query._bot = self._bot
            if self.callback_query.message:
                self.callback_query.message._bot = self._bot

    @property
    def type(self) -> Optional[str]:
        """Get the type of update (message/callback_query)"""
        if self.message:
            return "message"
        if self.callback_query:
            return "callback_query"
        return None

    @property
    def origin(self) -> Union[Message, CallbackQuery, None]:
        """Get the origin object of the update"""
        return self.message or self.callback_query

    def __getitem__(self, key: str) -> Any:
        """Get item from data dictionary"""
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item in data dictionary"""
        self.data[key] = value

    def __str__(self) -> str:
        """String representation of the update"""
        origin_info = ""
        if self.origin:
            if isinstance(self.origin, Message):
                origin_info = (
                    f", text={self.origin.text[:20]}..." if self.origin.text else ""
                )
            elif isinstance(self.origin, CallbackQuery):
                origin_info = f", data={self.origin.data}" if self.origin.data else ""

        return f"Update(id={self.update_id}, type={self.type}{origin_info})"

    def _set_bot(self, bot_instance: Bot) -> None:
        """Alternative method to set bot (backward compatibility)"""
        self.bot = bot_instance
