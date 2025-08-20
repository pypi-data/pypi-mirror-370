import asyncio
import logging
import socket
import threading

from decentnet.consensus.block_sizing import BLOCK_PREFIX_LENGTH_BYTES
from decentnet.consensus.blockchain_params import BlockchainParams
from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.consensus.dev_constants import (BLOCK_SHARE_LOG_LEVEL,
                                               RUN_IN_DEBUG)
from decentnet.consensus.share_server_config import (INCOMING_CHANNEL_BYTE_LEN,
                                                     SUBSCRIBE_ACK,
                                                     UNSUB_BYTE_LEN,
                                                     UNSUB_BYTE_STRING)
from decentnet.modules.convert.byte_to_base64_utils import bytes_to_base64
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.tcp.socket_functions import recv_all

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG if BLOCK_SHARE_LOG_LEVEL == logging.DEBUG else False, logger)
ADDR_ZERO = b"\x00" * 32


class BlockShareServer:
    def __init__(self, host='localhost', port1=8009, port2=8010):
        # First listener for storing addresses
        self.server_socket_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket_1.bind((host, port1))
        self.server_socket_1.listen(BlockchainParams.max_hosts)

        # Second listener for sending data to address
        self.server_socket_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket_2.bind((host, port2))
        self.server_socket_2.listen(BlockchainParams.max_hosts)

        # Dictionary to store address mappings
        self.address_dict = {}

        logger.debug(
            f"BlockShareServer started at {host}:{port1} for storing addresses and {host}:{port2} for sending data.")

    def listener_store_address(self):
        """ First listener: Store hash/socket pairs in dictionary """
        while True:
            conn, client_address = self.server_socket_1.accept()
            logger.debug(f"Accepting consumer {client_address}")
            threading.Thread(target=self.handle_consumer, args=(conn,), daemon=True,
                             name="Handling consumer").start()

    def handle_consumer(self, socket_obj: socket.socket):
        channel_bytes = socket_obj.recv(INCOMING_CHANNEL_BYTE_LEN)
        channel = bytes_to_base64(channel_bytes)

        if self.address_dict.get(channel) is None:
            logger.debug(f"Writing first subscriber {channel}")
        else:
            logger.debug(f"Overwriting {channel}")

        self.address_dict[channel] = socket_obj

        socket_obj.sendall(SUBSCRIBE_ACK)
        logger.debug(f"Current address dictionary looks like {tuple(self.address_dict.keys())}")
        try:
            cmd = socket_obj.recv(UNSUB_BYTE_LEN)
        except ConnectionResetError:
            logger.debug(f"Failed got {cmd}")
            cmd = UNSUB_BYTE_STRING

        if cmd == UNSUB_BYTE_STRING:
            logger.debug(f"Unsubscribed {channel}")
            self.address_dict.pop(socket_obj, None)
            socket_obj.close()

    def listener_send_data(self):
        """ Second listener: Send data to the socket identified by hash key """
        while True:
            conn, client_address = self.server_socket_2.accept()
            logger.debug(f"Accepting publisher {client_address}")
            threading.Thread(target=self.handle_publisher, args=(conn,), daemon=True,
                             name="Publisher handler").start()

    def handle_publisher(self, socket_obj: socket.socket):
        data_len = 1

        while data_len:
            try:
                raw_data, data_len = asyncio.run(recv_all(socket_obj))
                channel = bytes_to_base64(raw_data[:INCOMING_CHANNEL_BYTE_LEN])

                # Recompute length prefix to send only necessary data
                data = raw_data[INCOMING_CHANNEL_BYTE_LEN:]
                length_prefix = int.to_bytes(data_len - INCOMING_CHANNEL_BYTE_LEN,
                                             length=BLOCK_PREFIX_LENGTH_BYTES,
                                             byteorder=ENDIAN_TYPE, signed=False)

                logger.debug(f"Publisher sending data to {channel}")
                if (soc := self.address_dict.get(channel)) is not None:
                    soc.sendall(length_prefix + data)
            except ConnectionResetError:
                logger.debug("Publisher disconnected.")
                break

    def start(self):
        """ Start both listeners using threading """
        thread_1 = threading.Thread(target=self.listener_store_address, daemon=True, name="Address Store")
        # Start both listeners
        thread_1.start()

        # Wait for both threads to complete (they run indefinitely)

        self.listener_send_data()
        thread_1.join()


def start_block_share_server():
    server = BlockShareServer()
    server.start()


if __name__ == "__main__":
    start_block_share_server()
