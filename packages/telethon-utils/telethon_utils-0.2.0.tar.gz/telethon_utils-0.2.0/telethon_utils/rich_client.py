import asyncio
from typing import Optional

from telethon import (  # type: ignore
    TelegramClient,  # type: ignore
    functions,
    types,
)
from telethon.errors import UserAlreadyParticipantError  # type: ignore

from .errors import JoinFailed


class RichTelegramClient(TelegramClient):  # type: ignore
    me: Optional[types.User]
    phone_number: str
    ratelimited: bool

    # private attrs
    _rich_init_done: bool = False

    async def rich_init(self) -> None:
        if not self._rich_init_done:
            self._rich_init_done = True
            me = await self.get_me()
            assert isinstance(me, types.User)
            self.me = me

    @property
    def user_id(self) -> int:
        assert isinstance(self.me, types.User), "Client User not available"
        return int(self.me.id)

    @property
    def repr(self) -> str:
        """Something that can be represented on terminal"""
        if isinstance(self.me, types.User):
            if self.me.username:
                return "@" + str(self.me.username)

            if self.me.phone:
                return str(self.me.phone)

            if self.me.first_name:
                return str(self.me.first_name)

        return ""

    def link_to_slug(self, link: str) -> str:
        return link.split("/")[-1].replace("@", "").replace("+", "")

    async def check_chat_invite_link(
        self, link: str
    ) -> types.ChatInviteAlready | types.ChatInvite:
        result = await self(  # pyright:  ignore
            functions.messages.CheckChatInviteRequest(  # pyright: ignore
                hash=self.link_to_slug(link)
            )
        )
        assert isinstance(result, (types.ChatInviteAlready, types.ChatInvite))
        return result

    async def join_public_entity(self, entity_slug: str) -> int:
        """Join a public channel or group"""
        entity_slug = self.link_to_slug(entity_slug)
        resp: types.Updates = await self(  # pyright: ignore
            functions.channels.JoinChannelRequest(entity_slug)  # type: ignore
        )

        if resp.updates:  # pyright: ignore
            for update in resp.updates:  # pyright: ignore
                if isinstance(update, types.UpdateChannel):
                    return int(update.channel_id)

        else:
            # Updates is empty. Let's look for chats
            for chat in resp.chats:  # pyright: ignore
                if isinstance(chat, (types.Chat, types.Channel)):
                    return int(chat.id)

        raise JoinFailed(f"Failed to join public entity. Telegram says: {resp}")

    async def join_private_entity(self, entity_slug: str) -> int:
        entity_slug = self.link_to_slug(entity_slug)
        try:
            resp: types.Updates = await self(  # pyright: ignore
                functions.messages.ImportChatInviteRequest(entity_slug)
            )
            updates: list[  # pyright: ignore
                types.UpdateMessageID | types.UpdateChatParticipants
            ] = resp.updates  # pyright: ignore  # pyright: ignore
            for update in updates:  # pyright: ignore
                if isinstance(update, types.UpdateChatParticipants):
                    chat_id = update.participants.chat_id
                    return int(chat_id)

                if isinstance(update, types.UpdateChannel):
                    return int(update.channel_id)

            else:
                raise JoinFailed(
                    f"Failed to join private entity. Telegram says: {resp}"
                )

        except UserAlreadyParticipantError:
            res = await self.check_chat_invite_link(entity_slug)
            assert isinstance(res, types.ChatInviteAlready), (
                "Invalid response from chat Invite"
            )
            return int(res.chat.id)

    async def is_private_entity_link(self, link: str) -> bool:
        if "joinchat" in link:
            return True
        return link.split("/")[-1].replace("@", "").startswith("+")

    async def join_entity(self, entity_link: str) -> int:
        if await self.is_private_entity_link(entity_link):
            return await self.join_private_entity(entity_link)

        return await self.join_public_entity(entity_link)

    async def ratelimit_for(self, time: int) -> None:
        self.ratelimited = True

        async def _reset_after() -> None:
            await asyncio.sleep(time)
            self.ratelimited = False

        asyncio.create_task(_reset_after())
