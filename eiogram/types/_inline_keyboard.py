from dataclasses import dataclass
from typing import Optional, List
from ._base import BotModel


@dataclass
class InlineKeyboardButton(BotModel):
    text: str
    callback_data: Optional[str] = None
    url: Optional[str] = None
    web_app: Optional[str] = None
    copy_text: Optional[str] = None
    switch_inline_query_current_chat: Optional[str] = None

    def model_dump(self, exclude_none=False) -> dict:
        result = {"text": self.text}
        if self.callback_data is not None:
            result["callback_data"] = self.callback_data
        if self.url is not None:
            result["url"] = self.url
        if self.web_app is not None:
            result["web_app"] = {"url": self.web_app}
        if self.copy_text is not None:
            result["copy_text"] = {"text": self.copy_text}
        if self.switch_inline_query_current_chat is not None:
            result["switch_inline_query_current_chat"] = self.switch_inline_query_current_chat
        return result


@dataclass
class InlineKeyboardMarkup(BotModel):
    inline_keyboard: List[List[InlineKeyboardButton]]

    def dict(self) -> dict:
        return {"inline_keyboard": [[button.dict() for button in row] for row in self.inline_keyboard]}
