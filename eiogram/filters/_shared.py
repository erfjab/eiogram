from ._base import Filter


class ShareUser(Filter):
    def __init__(self):
        super().__init__(lambda msg: (hasattr(msg, "users_shared") and msg.users_shared is not None))


class ShareChat(Filter):
    def __init__(self):
        super().__init__(lambda msg: (hasattr(msg, "chat_shared") and msg.chat_shared is not None))
