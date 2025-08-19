import asyncio
import os
from typing import Optional

from proxy_reader.protocols.reader import ProxiesReaderProtocol  # type: ignore
from proxy_reader.reader import ProxiesReader  # type: ignore

from .enums import ProxyFormat, ProxyType  # type: ignore
from .rich_client import RichTelegramClient  # type: ignore
from .types import ClientsList  # type: ignore


def files_in_folder(folder: str) -> list[str]:
    path = ""
    filenames: list[str] = []
    for path, _, filenames in os.walk(folder):
        break
    return [f"{path}/{filename}" for filename in filenames]


async def phones_from_sessions_dir(dir: str) -> list[str]:
    files = files_in_folder(dir)
    return files


async def get_clients(
    sessions_dir: str,
    api_id: int,
    api_hash: str,
    proxies_reader: Optional[ProxiesReaderProtocol] = None,
    proxy_type: ProxyType = ProxyType.HTTP,
    proxy_format: ProxyFormat = ProxyFormat.IP_PORT_USER_PASS,
) -> ClientsList:
    if not proxies_reader:
        proxies_reader = ProxiesReader("proxies.txt")

    if proxy_format == ProxyFormat.IP_PORT:
        proxies_reader.read_authless()

    if proxy_format == ProxyFormat.IP_PORT_USER_PASS:
        proxies_reader.read_with_auth()

    proxies_reader.working_proxies = proxies_reader.proxies

    session_files = await phones_from_sessions_dir(sessions_dir)

    print(f"Loaded {len(session_files)} session files from {sessions_dir} ...")

    clients: ClientsList = []

    session_file_replacements: list[str] = [
        ".session--journal",
        ".session",
        "-journal",
        "-journal",
        ".",
    ]

    done: list[str] = []

    for s_file in session_files:
        for rep in session_file_replacements:
            s_file = s_file.replace(rep, "").strip()
        phone = s_file.split("/")[-1].strip()
        if phone in done:
            continue
        done.append(phone)

        print(f"Logging-in {phone} ...")

        p = (
            proxies_reader.next_http_telegram_from_cycle()
            if proxies_reader.proxies
            else None
        )
        client = RichTelegramClient(
            s_file,
            api_id=api_id,
            api_hash=api_hash,
            proxy=p,
        )

        try:
            await client.connect()  # pyright: ignore
            if await client.is_user_authorized():
                clients.append(client)
                print(f"[{phone}] login success!")
                await client.rich_init()
            else:
                print(f"[{phone}] session file not authorized!")

        except Exception as e:
            print(f"Failed to login {s_file}. {e}")

    return clients


async def close_client(client: RichTelegramClient | TelegramClient) -> None:
    try:
        await client.disconnect()  # type: ignore
        print("Client disconnected!")

    except ConnectionError:
        pass

    except Exception as e:
        print(f"Failed to disconnect client. {e}")


async def close_clients(clients: ClientsList) -> None:
    print("Disconnecting clients ...")
    async with asyncio.TaskGroup() as tg:
        for client in clients:
            tg.create_task(close_client(client))

    print("All clients disconnected!")
