
from enum import Enum, auto



class ProxyType(Enum):

    HTTP = auto()
    SOCKS4 = auto()
    SOCKS5 = auto()

class ProxyFormat(Enum):

    IP_PORT = auto()
    IP_PORT_USER_PASS = auto()