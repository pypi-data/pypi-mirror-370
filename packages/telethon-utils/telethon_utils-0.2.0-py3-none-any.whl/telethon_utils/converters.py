from typing import cast

from telethon import events, types  # type: ignore
from telethon.tl.custom import Message as CustomMessage  # type: ignore


def link_to_uid(link: str) -> str:
    """
    Convert telegram link to uid
    uid is referred as a username, private channel join hash etc
    i.e. https://t.me/runetech  -> runetech
    i.e. @runetech -> runetech"""
    return link.split("?")[0].split("/")[-1].replace("@", "")


def links_to_uids(links: list[str]) -> list[str]:
    """Same as link to uid but works with a list instead"""
    uids: list[str] = []

    for link in links:
        uids.append(link_to_uid(link))

    return uids


def message_ev_to_custom_message_ob(e: events.NewMessage.Event) -> CustomMessage:
    return cast(CustomMessage, e.message)


def message_to_custom_message(m: types.Message) -> CustomMessage:
    return cast(CustomMessage, m)
