from typing import Optional
from ._base import BotModel


class Contact(BotModel):
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    user_id: Optional[int] = None

    def __str__(self) -> str:
        return f"Contact(phone_number={self.phone_number}, first_name={self.first_name})"
