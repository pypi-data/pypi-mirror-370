from enum import Enum


class NetworkCmd(Enum):
    """Enum of commands"""
    HANDSHAKE_ENCRYPTION = 0
    BROADCAST = 1  # Broadcast new connection
    SYNCHRONIZE = 2
    DISCONNECT_EDGE = 3  # R2R Comm extended
    REDELIVER_ON_CONNECT = 4
