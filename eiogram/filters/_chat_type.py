from ._base import Filter


class ChatTypeFilter(Filter):
    """Base class for chat type filters"""

    def __init__(self, chat_type: str):
        super().__init__(
            lambda msg: (
                hasattr(msg, "chat")
                and hasattr(msg.chat, "type")
                and msg.chat.type == chat_type
            )
        )


class IsPrivate(ChatTypeFilter):
    def __init__(self):
        super().__init__("private")


class IsGroup(ChatTypeFilter):
    def __init__(self):
        super().__init__("group")


class IsSuperGroup(ChatTypeFilter):
    def __init__(self):
        super().__init__("supergroup")


class IsChannel(ChatTypeFilter):
    def __init__(self):
        super().__init__("channel")


class IsForum(ChatTypeFilter):
    def __init__(self):
        super().__init__("forum")
