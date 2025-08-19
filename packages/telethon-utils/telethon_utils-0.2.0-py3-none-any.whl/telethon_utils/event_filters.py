from typing import Any, Callable, Coroutine, Optional, cast

from telethon import events  # type: ignore

from .extractors import get_user_id_from_callback_query, get_user_id_from_message_event


def query_data_starts_with(
    starts_with: str, from_user: Optional[int] = None
) -> Callable[[events.CallbackQuery.Event], Coroutine[Any, Any, bool]]:
    async def inner(e: events.CallbackQuery.Event) -> bool:
        if from_user:
            user_id = get_user_id_from_callback_query(e)
            if user_id != from_user:
                return False
        return str(e.query.data.decode()).startswith(starts_with)  # pyright: ignore

    return inner


def chat_message(
    chats_id: int,
) -> Callable[[events.NewMessage.Event], Coroutine[Any, Any, bool]]:
    async def inner(e: events.NewMessage.Event) -> bool:
        chat_id = cast(int, e.chat_id)  # pyright: ignore
        return chat_id == chats_id

    return inner


def message_from_chatslist(
    chat_ids: list[int],
) -> Callable[[events.NewMessage.Event], Coroutine[Any, Any, bool]]:
    async def inner(e: events.NewMessage.Event) -> bool:
        chat_id = cast(int, e.chat_id)  # pyright: ignore
        return chat_id in chat_ids

    return inner


def private_command(
    command: str, from_users: list[int] = []
) -> Callable[[events.NewMessage.Event], Coroutine[Any, Any, bool]]:
    async def inner(e: events.NewMessage.Event) -> bool:
        user_id = get_user_id_from_message_event(e)
        if from_users and user_id not in from_users:
            return False

        m = cast(str, e.message.message)  # pyright: ignore
        return m.startswith(command)

    return inner


def public_command(
    command: str,
) -> Callable[[events.NewMessage.Event], Coroutine[Any, Any, bool]]:
    async def inner(e: events.NewMessage.Event) -> bool:
        m = cast(str, e.message.message)  # pyright: ignore
        return m.startswith(command)

    return inner
