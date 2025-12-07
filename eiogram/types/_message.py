from enum import StrEnum
from typing import Optional, Union, List
from pydantic import Field
from ._base import BotModel
from ._user import User
from ._chat import Chat
from ._contact import Contact
from ._inline_keyboard import InlineKeyboardMarkup
from ._shared import UsersShared, ChatShared


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
    BLOCKQUOTE = "blockquote"
    BANK_CARD = "bank_card"
    CUSTOM_EMOJI = "custom_emoji"


class PhotoSize(BotModel):
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None


class MessageEntity(BotModel):
    type: str
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional["User"] = None
    language: Optional[str] = None
    custom_emoji_id: Optional[str] = None


class Message(BotModel):
    message_id: int
    from_user: Optional[User] = Field(None, alias="from")
    chat: Chat
    text: Optional[str] = None
    photo: Optional[list[PhotoSize]] = None
    caption: Optional[str] = None
    caption_entities: Optional[List[MessageEntity]] = None
    entities: Optional[List[MessageEntity]] = None
    users_shared: Optional[UsersShared] = None
    chat_shared: Optional[ChatShared] = None
    contact: Optional[Contact] = None
    forward_from: Optional[User] = None
    forward_from_chat: Optional[Chat] = None
    forward_from_message_id: Optional[int] = None
    forward_signature: Optional[str] = None
    forward_sender_name: Optional[str] = None
    forward_date: Optional[int] = None

    @property
    def id(self) -> int:
        return self.message_id

    @property
    def is_forward(self) -> bool:
        return bool(self.forward_date)

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
        photo: Union[str, bytes],
        caption: Optional[str] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
    ) -> "Message":
        return await self.bot.send_photo(
            chat_id=self.chat.id,
            photo=photo,
            caption=caption,
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

    async def edit(
        self,
        text: str,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
    ) -> "Message":
        if self.photo:
            return await self.bot.edit_message_caption(
                chat_id=self.chat.id,
                message_id=self.message_id,
                caption=text,
                reply_markup=reply_markup,
            )

        return await self.bot.edit_message(
            chat_id=self.chat.id,
            message_id=self.message_id,
            text=text,
            reply_markup=reply_markup,
        )

    async def edit_text(
        self,
        text: str,
    ) -> "Message":
        if self.photo:
            return await self.bot.edit_message_caption(
                chat_id=self.chat.id,
                message_id=self.message_id,
                caption=text,
            )

        return await self.bot.edit_message_text(
            chat_id=self.chat.id,
            message_id=self.message_id,
            text=text,
        )

    async def edit_reply_markup(
        self,
        reply_markup: "InlineKeyboardMarkup",
    ) -> "Message":
        return await self.bot.edit_message_reply_markup(
            chat_id=self.chat.id,
            message_id=self.message_id,
            reply_markup=reply_markup,
        )

    async def delete(self) -> bool:
        return await self.bot.delete_messages(chat_id=self.chat.id, message_ids=[self.message_id])

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
