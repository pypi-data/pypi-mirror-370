from telethon.events import CallbackQuery  # type: ignore
from telethon.tl.custom import Button  # type: ignore
from telethon.types import KeyboardButtonCallback  # type: ignore


def data_button(text: str, data: bytes | str) -> KeyboardButtonCallback:
    if isinstance(data, str):
        data = data.encode()
    return Button.inline(text=text, data=data)  # type: ignore


def join_query(prefix: str, data: str) -> str:
    return f"{prefix}:{data}"


def split_query(data: str | bytes) -> list[str]:
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    return data.split(":")


def extract_query_data(e: CallbackQuery.Event, remove_prefix: bool = True) -> str:
    data = e.query.data.decode()  # type: ignore
    if remove_prefix:
        return split_query(data)[-1]  # type: ignore
    return str(data)  # type: ignore


def pack_query_data(data: list[str]) -> bytes:
    return ":".join(data).encode("utf-8")


def unpack_query_data(data: bytes, remove_first: bool = False) -> list[str]:
    _unpacked = data.decode("utf-8").split(":")
    if remove_first:
        del _unpacked[0]

    return _unpacked


def create_back_data(data: list[str], back_prefix: str) -> bytes:
    _data = data.copy()
    _data[0] = back_prefix
    del _data[-1]
    return pack_query_data(_data)
