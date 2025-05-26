from enum import StrEnum
from typing import Optional, Union, List
from pydantic import BaseModel, Field
from ._user import User
from ._chat import Chat
from ._inline_keyboard import InlineKeyboardMarkup
from ..client import Bot


class EntityType(StrEnum):
    MENTION = "mention"
    HASHTAG = "hashtag"
    CASHTAG = "cashtag"
    BOT_COMMAND = "bot_command"
    URL = "url"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    BOLD = "bold"
    ITALIC = "italic"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    SPOILER = "spoiler"
    CODE = "code"
    PRE = "pre"
    TEXT_LINK = "text_link"
    TEXT_MENTION = "text_mention"


class PhotoSize(BaseModel):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None


class MessageEntity(BaseModel):
    type: EntityType
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional["User"] = None


class Message(BaseModel):
    message_id: int
    from_user: User = Field(..., alias="from")
    chat: Chat
    text: Optional[str] = None
    photo: Optional[list[PhotoSize]] = None
    caption: Optional[str] = None
    caption_entities: Optional[List[MessageEntity]] = None
    bot: Optional[Bot] = None
    entities: Optional[List[MessageEntity]] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True

    @property
    def id(self) -> int:
        return self.message_id

    @property
    def context(self) -> Optional[str]:
        return self.text or self.caption

    def __str__(self) -> str:
        media_info = f", media={self.photo[0].file_id}" if self.photo else ""
        return f"Message(id={self.id}, text={self.context or 'None'}{media_info})"

    def html_text(self) -> str:
        from ..utils.html_parse import MessageParser

        return MessageParser.parse_to_html(
            text=self.context or "",
            entities=self.entities or self.caption_entities,
        )

    async def is_join(
        self,
        chat_id: Union[str, int],
    ) -> bool:
        from ._chat import ChatMemberStatus

        status = await self.bot.get_chat_member(chat_id=chat_id, user_id=self.chat.id)
        if status and status in [
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.RESTRICTED,
        ]:
            return True
        return False

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

    async def answer_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[str, bytes],
        caption: Optional[str] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
    ) -> "Message":
        return await self.bot.send_photo(
            chat_id=chat_id, photo=photo, caption=caption, reply_markup=reply_markup
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
