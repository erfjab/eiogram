from dataclasses import dataclass
from typing import Optional, List, Union
from ._base import BotModel
from ._user import User
from ._inline_keyboard import InlineKeyboardMarkup


@dataclass
class InlineQuery(BotModel):
    id: str
    from_user: User
    query: str = ""
    offset: str = ""
    chat_type: Optional[str] = None

    _aliases = {"from_user": "from"}

    def __str__(self) -> str:
        return f"InlineQuery(id={self.id}, from={self.from_user.full_name}, query={self.query})"


@dataclass
class InputTextMessageContent(BotModel):
    message_text: str
    parse_mode: Optional[str] = "HTML"
    disable_web_page_preview: Optional[bool] = None


@dataclass(kw_only=True)
class InlineQueryResult(BotModel):
    type: str
    id: str


@dataclass(kw_only=True)
class InlineQueryResultArticle(InlineQueryResult):
    title: str
    input_message_content: InputTextMessageContent
    type: str = "article"
    reply_markup: Optional[InlineKeyboardMarkup] = None
    url: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None


@dataclass(kw_only=True)
class InlineQueryResultPhoto(InlineQueryResult):
    photo_url: str
    thumb_url: str
    type: str = "photo"
    photo_width: Optional[int] = None
    photo_height: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = "HTML"
    reply_markup: Optional[InlineKeyboardMarkup] = None


InlineQueryResultType = Union[InlineQueryResultArticle, InlineQueryResultPhoto]


@dataclass
class AnswerInlineQuery(BotModel):
    inline_query_id: str
    results: List[InlineQueryResultType]
    cache_time: int = 300
