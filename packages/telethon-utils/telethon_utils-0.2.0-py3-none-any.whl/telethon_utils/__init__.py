from typing import Never
from telethon import events
from .rich_client import *
from .emojis import *

__version__ = "0.1.0"


def stop_event() -> Never:
    raise events.StopPropagation
