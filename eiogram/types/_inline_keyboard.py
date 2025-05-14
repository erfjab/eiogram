from dataclasses import dataclass
from typing import Optional, List
from ._base import Validated


@dataclass
class InlineKeyboardButton(Validated):
    text: str
    callback_data: Optional[str]
    url: Optional[str] = None
    web_app: Optional[str] = None
    copy_text: Optional[str] = None
    switch_inline_query: Optional[str] = None

    def dict(self) -> dict:
        return {
            k: v
            for k, v in {
                "text": self.text,
                "callback_data": self.callback_data,
                "url": self.url,
                "web_app": self.web_app,
                "copy_text": self.copy_text,
                "switch_inline_query": self.switch_inline_query,
            }.items()
            if v is not None
        }


@dataclass
class InlineKeyboardMarkup:
    inline_keyboard: List[List[InlineKeyboardButton]]

    def dict(self) -> dict:
        return {
            "inline_keyboard": [
                [button.dict() for button in row] for row in self.inline_keyboard
            ]
        }
