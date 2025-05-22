from ._base import Filter


class _ChatTypeFilter(Filter):
    """Base class for chat type filters"""

    def __init__(self, chat_type: str):
        super().__init__(
            lambda msg: (
                hasattr(msg, "chat")
                and hasattr(msg.chat, "type")
                and msg.chat.type == chat_type
            )
        )


class IsPrivate(_ChatTypeFilter):
    def __init__(self):
        super().__init__("private")


class IsGroup(_ChatTypeFilter):
    def __init__(self):
        super().__init__("group")


class IsSuperGroup(_ChatTypeFilter):
    def __init__(self):
        super().__init__("supergroup")


class IsChannel(_ChatTypeFilter):
    def __init__(self):
        super().__init__("channel")


class IsForum(_ChatTypeFilter):
    def __init__(self):
        super().__init__("forum")
