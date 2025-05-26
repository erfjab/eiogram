from typing import List, Optional, TYPE_CHECKING
from html import escape

if TYPE_CHECKING:
    from ..types._message import MessageEntity, EntityType


class MessageParser:
    @staticmethod
    def parse_to_html(
        text: str, entities: Optional[List["MessageEntity"]] = None
    ) -> str:
        if not text:
            return ""
        if not entities:
            return escape(text)
        entities = sorted(entities, key=lambda e: e.offset)
        tags = []
        html_parts = []
        last_pos = 0

        for entity in entities:
            if (
                entity.offset < 0
                or entity.length <= 0
                or entity.offset + entity.length > len(text)
            ):
                continue

            if entity.offset > last_pos:
                html_parts.append(escape(text[last_pos : entity.offset]))
                last_pos = entity.offset

            start_tag = MessageParser._get_html_start_tag(entity)
            if start_tag:
                tags.append(
                    (
                        entity.offset + entity.length,
                        MessageParser._get_html_end_tag(entity),
                    )
                )
                html_parts.append(start_tag)

            html_parts.append(
                escape(text[entity.offset : entity.offset + entity.length])
            )

        if last_pos < len(text):
            html_parts.append(escape(text[last_pos:]))

        for pos, end_tag in sorted(tags, reverse=True):
            html_parts.insert(pos, end_tag)

        return "".join(html_parts)

    @staticmethod
    def _get_html_start_tag(entity: "MessageEntity") -> str:
        mapping = {
            EntityType.BOLD: "<b>",
            EntityType.ITALIC: "<i>",
            EntityType.UNDERLINE: "<u>",
            EntityType.STRIKETHROUGH: "<s>",
            EntityType.SPOILER: "<span class='tg-spoiler'>",
            EntityType.CODE: "<code>",
            EntityType.PRE: "<pre>",
        }
        if entity.type == EntityType.TEXT_LINK and entity.url:
            return f"<a href='{escape(entity.url)}'>"
        return mapping.get(entity.type, "")

    @staticmethod
    def _get_html_end_tag(entity: "MessageEntity") -> str:
        mapping = {
            EntityType.BOLD: "</b>",
            EntityType.ITALIC: "</i>",
            EntityType.UNDERLINE: "</u>",
            EntityType.STRIKETHROUGH: "</s>",
            EntityType.SPOILER: "</span>",
            EntityType.CODE: "</code>",
            EntityType.PRE: "</pre>",
            EntityType.TEXT_LINK: "</a>",
        }
        return mapping.get(entity.type, "")
