from ._base import Filter


class Photo(Filter):
    def __init__(self):
        super().__init__(
            lambda msg: (
                hasattr(msg, "photo") and msg.photo is not None and bool(msg.photo)
            )
        )
