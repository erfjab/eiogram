from ._base import Filter


class Data(Filter):
    def __init__(self, data: str):
        super().__init__(
            lambda cb: (hasattr(cb, "data") and getattr(cb, "data", None) == data)
        )
