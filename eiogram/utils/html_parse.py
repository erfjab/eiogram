from typing import List, Optional, TYPE_CHECKING
from html import escape

if TYPE_CHECKING:
    from ..types._message import MessageEntity

from ..types._message import EntityType

_START_TAG = 1
_END_TAG = 0

_START_TAGS: dict[str, str] = {
    EntityType.BOLD: "<b>",
    EntityType.ITALIC: "<i>",
    EntityType.UNDERLINE: "<u>",
    EntityType.STRIKETHROUGH: "<s>",
    EntityType.SPOILER: "<tg-spoiler>",
    EntityType.CODE: "<code>",
    EntityType.PRE: "<pre>",
    EntityType.BLOCKQUOTE: "<blockquote>",
}

_END_TAGS: dict[str, str] = {
    EntityType.BOLD: "</b>",
    EntityType.ITALIC: "</i>",
    EntityType.UNDERLINE: "</u>",
    EntityType.STRIKETHROUGH: "</s>",
    EntityType.SPOILER: "</tg-spoiler>",
    EntityType.CODE: "</code>",
    EntityType.PRE: "</pre>",
    EntityType.BLOCKQUOTE: "</blockquote>",
    EntityType.TEXT_LINK: "</a>",
    EntityType.TEXT_MENTION: "</a>",
    EntityType.CUSTOM_EMOJI: "</tg-emoji>",
}


class MessageParser:
    @staticmethod
    def _build_offset_map(text: str) -> dict[int, int]:
        offset_map = {}
        utf16_pos = 0
        for i, char in enumerate(text):
            offset_map[utf16_pos] = i
            utf16_pos += len(char.encode("utf-16-le")) // 2
        offset_map[utf16_pos] = len(text)
        return offset_map

    @staticmethod
    def _build_tokens(
        entities: List["MessageEntity"],
        offset_map: dict[int, int],
    ) -> list[tuple[int, int, int, "MessageEntity"]]:
        tokens = []
        for entity in entities:
            start_utf16 = entity.offset
            end_utf16 = entity.offset + entity.length

            if start_utf16 not in offset_map or end_utf16 not in offset_map:
                continue

            start_idx = offset_map[start_utf16]
            end_idx = offset_map[end_utf16]
            length = end_idx - start_idx

            tokens.append((start_idx, _START_TAG, -length, entity))
            tokens.append((end_idx, _END_TAG, length, entity))

        tokens.sort(key=lambda x: (x[0], x[1], x[2]))
        return tokens

    @staticmethod
    def parse_to_html(
        text: str,
        entities: Optional[List["MessageEntity"]] = None,
    ) -> str:
        """Convert text with Telegram entities to HTML."""
        if not text:
            return ""
        if not entities:
            return escape(text)

        offset_map = MessageParser._build_offset_map(text)
        tokens = MessageParser._build_tokens(entities, offset_map)

        html = []
        last_idx = 0

        for idx, tag_type, _, entity in tokens:
            if idx > last_idx:
                html.append(escape(text[last_idx:idx]))
                last_idx = idx

            if tag_type == _START_TAG:
                html.append(MessageParser._get_start_tag(entity))
            else:
                html.append(MessageParser._get_end_tag(entity))

        if last_idx < len(text):
            html.append(escape(text[last_idx:]))

        return "".join(html)

    @staticmethod
    def _get_start_tag(entity: "MessageEntity") -> str:
        if entity.type in _START_TAGS:
            return _START_TAGS[entity.type]

        if entity.type == EntityType.TEXT_LINK and entity.url:
            return f"<a href='{escape(entity.url)}'>"

        if entity.type == EntityType.TEXT_MENTION and entity.user:
            return f"<a href='tg://user?id={entity.user.id}'>"

        if entity.type == EntityType.CUSTOM_EMOJI:
            if entity.custom_emoji_id:
                return f"<tg-emoji emoji-id='{entity.custom_emoji_id}'>"
            return "<tg-emoji>"

        return ""

    @staticmethod
    def _get_end_tag(entity: "MessageEntity") -> str:
        return _END_TAGS.get(entity.type, "")
