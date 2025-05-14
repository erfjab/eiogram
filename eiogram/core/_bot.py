from typing import Optional, Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from eiogram.types._me import Me
    from eiogram.types._message import Message
    from eiogram.types._inline_keyboard import InlineKeyboardMarkup


class Bot:
    def __init__(self, token: str):
        self.token = token

    async def get_me(self) -> "Me":
        from eiogram.methods._get_me import GetMe

        return await GetMe(self.token).execute()

    async def set_webhook(
        self,
        url: str,
        max_connections: int = 40,
        allowed_updates: Optional[List[str]] = None,
        drop_pending_updates: bool = False,
        secret_token: Optional[str] = None,
    ) -> bool:
        from eiogram.methods._set_webhook import SetWebhook

        return await SetWebhook(self.token).execute(
            url=url,
            max_connections=max_connections,
            allowed_updates=allowed_updates,
            drop_pending_updates=drop_pending_updates,
            secret_token=secret_token,
        )

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
    ) -> "Message":
        from eiogram.methods._send_message import SendMessage

        return await SendMessage(self.token).execute(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
        )

    async def edit_message(
        self,
        chat_id: Union[int, str],
        message_id: int,
        text: str,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
    ) -> "Message":
        from eiogram.methods._edit_message import EditMessage

        return await EditMessage(self.token).execute(
            chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup
        )

    async def send_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[str, bytes],
        caption: Optional[str] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
    ) -> "Message":
        from eiogram.methods._send_photo import SendPhoto

        return await SendPhoto(self.token).execute(
            chat_id=chat_id, photo=photo, caption=caption, reply_markup=reply_markup
        )

    async def pin_message(
        self,
        chat_id: Union[int, str],
        message_id: int,
        disable_notification: bool = False,
    ) -> bool:
        from eiogram.methods._pin_message import PinMessage

        return await PinMessage(self.token).execute(
            chat_id=chat_id,
            message_id=message_id,
            disable_notification=disable_notification,
        )

    async def delete_messages(
        self, chat_id: Union[int, str], message_ids: List[int]
    ) -> List[bool]:
        from eiogram.methods._delete_messages import DeleteMessages

        return await DeleteMessages(self.token).execute(
            chat_id=chat_id, message_ids=message_ids
        )
