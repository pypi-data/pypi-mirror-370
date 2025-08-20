import logging
import os
import socket

from decentnet.consensus.block_sizing import BLOCK_PREFIX_LENGTH_BYTES
from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.consensus.dev_constants import (BLOCK_SHARE_LOG_LEVEL,
                                               RUN_IN_DEBUG)
from decentnet.modules.convert.byte_to_base64_utils import base64_to_original
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.tcp.socket_functions import set_sock_properties_common

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG if BLOCK_SHARE_LOG_LEVEL == logging.DEBUG else False, logger)


class Publisher:
    """
    Publisher class that sends data to a specific channel (hash key) via the server.
    """

    def __init__(self):
        self.server_host = "127.0.0.1"
        self.server_port = 8010  # 8010 ports are used for sending data to consumers
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        set_sock_properties_common(self.socket)
        self.socket.connect((self.server_host, self.server_port))

    async def __send_data(self, data):
        data_len = len(data)
        length_prefix = int.to_bytes(data_len, length=BLOCK_PREFIX_LENGTH_BYTES,
                                     byteorder=ENDIAN_TYPE, signed=False)
        logger.debug(
            "Outgoing message prefix %s | %s bytes, with prefix %s B" % (
                length_prefix.hex(), data_len, BLOCK_PREFIX_LENGTH_BYTES + data_len))

        self.socket.sendall(length_prefix + data)

    async def publish_message(self, channel: str, data: bytes) -> None:
        """
        Send a message to a specific channel (hash key) via the server.

        Args:
            channel (str): The hash key of the subscriber to which the message is to be sent.
            data (str): The message to send to the subscriber.
        """
        logger.debug("Publishing message to channel %s PID: %s}" % (channel, os.getpid()))
        channel_bytes = base64_to_original(channel)
        await self.__send_data(channel_bytes + data)
