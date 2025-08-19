from typing import cast

from telethon.events import CallbackQuery, NewMessage  # type: ignore
from telethon.events.common import EventCommon  # type: ignore
from telethon.types import Message as TelegramMessage  # type: ignore
from telethon.types import PeerUser, UpdateNewMessage  # type: ignore

from .rich_client import RichTelegramClient


def std_chat_id(chat_id: int) -> int:
    _id = str(chat_id)
    if _id.startswith("-100"):
        _id = _id[3:]

    if _id.startswith("-"):
        _id = _id[1:]

    return int(_id)


def get_message_obj_from_message_event(event: NewMessage.Event) -> TelegramMessage:
    """Extract typed message object from TelegramMessage"""
    orig_update = cast(UpdateNewMessage, event.original_update)
    return cast(TelegramMessage, orig_update.message)


def get_user_id_from_callback_query(e: CallbackQuery.Event) -> int:
    assert isinstance(e.sender_id, int), (  # type: ignore
        f"sender_id is not int in event. Type: {e.sender_id}"  # type: ignore
    )
    return int(e.sender_id)


def get_user_id_from_message_event(event: NewMessage.Event) -> int:
    pure_message = get_message_obj_from_message_event(event)
    assert isinstance(pure_message.peer_id, PeerUser), (  # type: ignore
        f"peer_id is not PeerUser in event. Type: {pure_message.peer_id}"
    )
    assert isinstance(pure_message.peer_id.user_id, int), (  # type: ignore
        f"user_id is not int in event. Type: {pure_message.peer_id.user_id}"
    )
    return pure_message.peer_id.user_id


def get_client_from_event(event: EventCommon) -> RichTelegramClient:
    return cast(RichTelegramClient, event.client)
