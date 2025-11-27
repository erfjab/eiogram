from ._base import Filter


class Contact(Filter):
    def __init__(self):
        super().__init__(lambda msg: (hasattr(msg, "contact") and msg.contact is not None))
