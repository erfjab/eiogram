from typing import Optional, List
from pydantic import BaseModel


class InlineKeyboardButton(BaseModel):
    text: str
    callback_data: Optional[str] = None
    url: Optional[str] = None
    web_app: Optional[str] = None
    copy_text: Optional[str] = None

    def dict(self) -> dict:
        result = {"text": self.text}
        if self.callback_data is not None:
            result["callback_data"] = self.callback_data
        if self.url is not None:
            result["url"] = self.url
        if self.web_app is not None:
            result["web_app"] = {"url": self.web_app}
        if self.copy_text is not None:
            result["copy_text"] = {"text": self.copy_text}
        return result


class InlineKeyboardMarkup(BaseModel):
    inline_keyboard: List[List[InlineKeyboardButton]]

    def dict(self) -> dict:
        return {
            "inline_keyboard": [
                [button.dict() for button in row] for row in self.inline_keyboard
            ]
        }
