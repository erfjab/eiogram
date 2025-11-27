from typing import Optional, List
from pydantic import BaseModel


class SharedUser(BaseModel):
    user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo: Optional[List[dict]] = None

    @property
    def id(self) -> int:
        return self.user_id

    @property
    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or ""


class UsersShared(BaseModel):
    request_id: int
    users: List[SharedUser]

    @property
    def user_ids(self) -> List[int]:
        return [user.user_id for user in self.users]

    @property
    def first_user(self) -> Optional[SharedUser]:
        return self.users[0] if self.users else None


class ChatShared(BaseModel):
    request_id: int
    chat_id: int
    title: Optional[str] = None
    username: Optional[str] = None
    photo: Optional[List[dict]] = None

    @property
    def id(self) -> int:
        return self.chat_id
