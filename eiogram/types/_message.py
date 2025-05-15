from dataclasses import dataclass
from typing import Optional, List, Union
from ._chat import Chat
from ._user import User
from ._inline_keyboard import InlineKeyboardMarkup
from ._base import Validated

from ..core._bot import Bot


@dataclass
class PhotoSize(Validated):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None


@dataclass
class Message(Validated):
    message_id: int
    chat: Chat
    from_user: Optional[User] = None
    text: Optional[str] = None
    caption: Optional[str] = None
    photo: Optional[List[PhotoSize]] = None
    _bot: Optional[object] = None

    @property
    def bot(self) -> Bot:
        if self._bot is None:
            raise AttributeError("Bot instance not set. Use Message.set_bot() first.")
        return self._bot

    def set_bot(self, bot):
        self._bot = bot

    @property
    def id(self) -> int:
        return self.message_id

    @property
    def context(self) -> Optional[str]:
        return self.text or self.caption

    @property
    def has_media(self) -> bool:
        return self.photo is not None

    def __str__(self) -> str:
        media_info = f", media={self.photo[0].file_id}" if self.photo else ""
        return f"Message(id={self.id}, text={self.context or 'None'}{media_info})"

    async def answer(
        self,
        text: str,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
    ) -> "Message":
        return await self.bot.send_message(
            chat_id=self.chat.id,
            text=text,
            reply_markup=reply_markup,
        )

    async def reply(
        self,
        text: str,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
    ) -> "Message":
        return await self.bot.send_message(
            chat_id=self.chat.id,
            text=text,
            reply_markup=reply_markup,
            reply_to_message_id=self.message_id,
        )

    async def answer_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[str, bytes],
        caption: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> "Message":
        return await self.bot.send_photo(
            chat_id=chat_id, photo=photo, caption=caption, reply_markup=reply_markup
        )

    async def edit(
        self,
        text: str,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
    ) -> "Message":
        return await self.bot.edit_message(
            chat_id=self.chat.id,
            message_id=self.message_id,
            text=text,
            reply_markup=reply_markup,
        )

    async def delete(self) -> bool:
        return await self.bot.delete_messages(
            chat_id=self.chat.id, message_ids=[self.message_id]
        )

    async def pin(self, disable_notification: bool = False) -> bool:
        return await self.bot.pin_message(
            chat_id=self.chat.id,
            message_id=self.message_id,
            disable_notification=disable_notification,
        )

    async def mute(self, until_date: int) -> bool:
        if self.from_user is None:
            return None
        return await self.bot.restrict_user(
            chat_id=self.chat.id,
            user_id=self.from_user.id,
            until_date=until_date,
        )
