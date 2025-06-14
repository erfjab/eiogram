from typing import Optional, List, Union
from pydantic import BaseModel, Field
from ._user import User
from ._inline_keyboard import InlineKeyboardMarkup


class InlineQuery(BaseModel):
    id: str
    from_user: User = Field(..., alias="from")
    query: str = ""
    offset: str = ""
    chat_type: Optional[str] = None

    class Config:
        validate_by_name = True
        arbitrary_types_allowed = True

    def __str__(self) -> str:
        return f"InlineQuery(id={self.id}, from={self.from_user.full_name}, query={self.query})"


class InputTextMessageContent(BaseModel):
    message_text: str
    parse_mode: Optional[str] = "HTML"
    disable_web_page_preview: Optional[bool] = None


class InlineQueryResult(BaseModel):
    type: str
    id: str


class InlineQueryResultArticle(InlineQueryResult):
    type: str = "article"
    title: str
    input_message_content: InputTextMessageContent
    reply_markup: Optional[InlineKeyboardMarkup] = None
    url: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None


class InlineQueryResultPhoto(InlineQueryResult):
    type: str = "photo"
    photo_url: str
    thumb_url: str
    photo_width: Optional[int] = None
    photo_height: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = "HTML"
    reply_markup: Optional[InlineKeyboardMarkup] = None


InlineQueryResultType = Union[InlineQueryResultArticle, InlineQueryResultPhoto]


class AnswerInlineQuery(BaseModel):
    inline_query_id: str
    results: List[InlineQueryResultType]
    cache_time: int = 300
