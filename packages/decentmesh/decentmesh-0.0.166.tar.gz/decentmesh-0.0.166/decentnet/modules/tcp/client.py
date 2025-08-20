import logging
import socket
from typing import Optional

import cbor2

from decentnet.consensus.block_sizing import (BLOCK_PREFIX_LENGTH_BYTES,
                                              MAXIMUM_DATA_SIZE)
from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.tcp.socket_functions import (recv_all,
                                                    set_sock_properties)

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class TCPClient:
    def __init__(self, host: Optional[str] = None, port: Optional[str] = None,
                 client_socket: Optional[socket.socket] = None, ip_type: Optional[int] = 4):
        if not client_socket:
            self.host = host
            self.port = port
            if ip_type == 4:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
            else:
                self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port, 0, 0))
            set_sock_properties(self.socket)
            logger.debug(f"Connected on {self.socket.getsockname()}")
        else:
            peer_name = client_socket.getpeername()
            self.host, self.port = peer_name[0], peer_name[1]
            self.socket = client_socket

    async def send_message(self, data: bytearray | bytes, ack=True) -> Optional[dict]:
        data_len = len(data)

        if data_len > MAXIMUM_DATA_SIZE:
            raise Exception("Too much data for one block, please split data to more blocks!")

        length_prefix = int.to_bytes(data_len, length=BLOCK_PREFIX_LENGTH_BYTES,
                                     byteorder=ENDIAN_TYPE, signed=False)
        logger.debug(
            f"Outgoing message prefix {length_prefix.hex()} | {data_len} bytes, with prefix {BLOCK_PREFIX_LENGTH_BYTES + data_len} B")
        try:
            self.socket.sendall(length_prefix + data)
        except OSError as e:
            logger.error(f"Socket error {e}")
        if ack:
            logger.debug("Waiting for acknowledgement...")
            response, response_len = await recv_all(self.socket, self.host, self.port)
            if response_len == 0:
                return None
            return cbor2.loads(response)

    async def receive_message(self, decode=True) -> bytes | bytearray | str:
        response, response_len = await recv_all(self.socket, self.host, self.port)
        logger.debug(
            f"Receiving message {response_len} bytes | tcp_wrapped")
        if decode:
            return cbor2.loads(response)
        else:
            return response

    def close(self):
        self.socket.close()
