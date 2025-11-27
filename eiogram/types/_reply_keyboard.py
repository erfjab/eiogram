from typing import Optional, List
from random import randint
from pydantic import BaseModel


class KeyboardButton(BaseModel):
    text: str
    request_contact: Optional[bool] = None
    request_location: Optional[bool] = None
    request_user: Optional[bool] = None
    request_channel: Optional[bool] = None
    request_group: Optional[bool] = None

    def dict(self) -> dict:
        result = {"text": self.text}

        if self.request_contact:
            result["request_contact"] = True
        elif self.request_location:
            result["request_location"] = True
        elif self.request_user:
            result["request_users"] = {
                "request_id": randint(1, 999999),
                "user_is_bot": False,
                "max_quantity": 1,
                "request_name": True,
                "request_username": True,
                "request_photo": True,
            }
        elif self.request_channel:
            result["request_chat"] = {
                "request_id": randint(1, 999999),
                "chat_is_channel": True,
                "request_title": True,
                "request_username": True,
                "request_photo": True,
            }
        elif self.request_group:
            result["request_chat"] = {
                "request_id": randint(1, 999999),
                "chat_is_channel": False,
                "request_title": True,
                "request_username": True,
                "request_photo": True,
            }

        return result


class ReplyKeyboardMarkup(BaseModel):
    keyboard: List[List[KeyboardButton]]
    resize_keyboard: Optional[bool] = None
    one_time_keyboard: Optional[bool] = None
    is_persistent: Optional[bool] = None
    input_field_placeholder: Optional[str] = None

    def dict(self) -> dict:
        result = {"keyboard": [[btn.dict() for btn in row] for row in self.keyboard]}

        if self.resize_keyboard is not None:
            result["resize_keyboard"] = self.resize_keyboard
        if self.one_time_keyboard is not None:
            result["one_time_keyboard"] = self.one_time_keyboard
        if self.is_persistent is not None:
            result["is_persistent"] = self.is_persistent
        if self.input_field_placeholder is not None:
            result["input_field_placeholder"] = self.input_field_placeholder

        return result


class ReplyKeyboardRemove(BaseModel):
    remove_keyboard: bool = True
    selective: Optional[bool] = None

    def dict(self) -> dict:
        result = {"remove_keyboard": self.remove_keyboard}
        if self.selective is not None:
            result["selective"] = self.selective
        return result
