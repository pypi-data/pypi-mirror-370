import logging
import socket

from decentnet.consensus.dev_constants import (BLOCK_SHARE_LOG_LEVEL,
                                               RUN_IN_DEBUG)
from decentnet.modules.convert.byte_to_base64_utils import base64_to_original
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.tcp.socket_functions import (recv_all,
                                                    set_sock_properties_common)

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG if BLOCK_SHARE_LOG_LEVEL == logging.DEBUG else False, logger)


class Subscriber:
    """
    Subscriber class that registers with the server and listens for messages on the same open socket.
    """

    def __init__(self):
        """
        Initialize the Subscriber with a hash key and server connection details.

        """
        self.channel = None
        self.server_host = "127.0.0.1"
        self.server_port = 8009  # 8009 is used for reporting address to block share server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        set_sock_properties_common(self.socket)
        self.socket.connect((self.server_host, self.server_port))

    def unsubscribe(self):
        logger.debug("Subscriber asking to unsubscribe from channel")
        self.socket.sendall(b"UNSUB")

    def subscribe(self, channel: str) -> bool:
        """
        Send the subscriber's hash to the server to register the socket.
        """
        self.channel = channel
        self.socket.sendall(base64_to_original(channel))
        # Receive confirmation from the server
        return self.socket.recv(2) == b"OK"

    async def consume(self) -> bytes:
        """
        Listen for incoming messages and consume them.
        This runs in a loop, receiving data from the server over the same socket.
        """
        logger.debug(f"Consumer {self.channel} is now listening for messages...")
        return (await recv_all(self.socket))[0]
