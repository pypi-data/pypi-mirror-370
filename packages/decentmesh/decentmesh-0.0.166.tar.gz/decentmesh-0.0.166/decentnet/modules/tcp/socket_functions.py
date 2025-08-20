import io
import logging
import os
import socket
import threading
from typing import Optional

from decentnet.consensus.block_sizing import BLOCK_PREFIX_LENGTH_BYTES
from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.tcp_params import RECV_BUFFER_SIZE, SEND_BUFFER_SIZE
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


def set_sock_properties(socket_obj: socket.socket):
    socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RECV_BUFFER_SIZE)
    socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SEND_BUFFER_SIZE)
    socket_obj.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)


async def recv_prefix(sock: socket.socket, length: int) -> memoryview:
    """
    Receive exactly `length` bytes from `sock`.
    Returns a memoryview over a bytearray that holds the data.
    Raises ConnectionError if the socket closes before we get all bytes.
    """
    if length <= 0:
        return memoryview(bytearray(0))  # or just return memoryview(b'')

    buf = bytearray(length)  # Pre-allocate exactly `length` bytes
    view = memoryview(buf)
    received = 0

    while received < length:
        n = sock.recv_into(view[received:], length - received)
        if n == 0:
            raise ConnectionError("Socket closed before reading required bytes.")
        received += n

    return view


async def recv_all(socket_obj: socket.socket, host: Optional[str] = None,
                   port: Optional[int] = None, length_prefix_size=BLOCK_PREFIX_LENGTH_BYTES) -> (
        tuple)[bytes, int]:
    """Receive all bytes of a message up to total_bytes from a socket."""
    if RUN_IN_DEBUG:
        logger.debug(
            f"Thread {threading.current_thread().name} in PID {os.getpid()} is reading socket {socket_obj}")

    try:
        length_prefix = await recv_prefix(socket_obj, length_prefix_size)
    except (ConnectionError, ConnectionResetError, ConnectionAbortedError,
            ConnectionRefusedError) as e:
        logger.debug(f"Beacon {host}:{port} forcefully disconnected")
        raise e

    total_bytes = int.from_bytes(length_prefix, ENDIAN_TYPE, signed=False)
    if total_bytes:
        if RUN_IN_DEBUG:
            logger.debug(
                f"Incoming message will have length {total_bytes} B |"
                f" prefix {length_prefix.hex()} | Thread: {threading.current_thread().name}")
    else:
        return b'', 0

    buffer = io.BytesIO()
    data_len = 0

    while data_len < total_bytes:
        # Calculate the remaining bytes to receive
        remaining_bytes = total_bytes - data_len

        # Receive up to the remaining number of bytes
        frame = socket_obj.recv(remaining_bytes)

        if not frame:
            # No more data is being sent; possibly the connection was closed
            logger.debug(
                f"Data is not being sent, closing connection... Remaining {remaining_bytes} Bytes "
                f"Thread: {threading.current_thread().name} | Buffer contained {buffer.getvalue()}")
            break

        # Write the received frame into the BytesIO buffer
        written_bytes = buffer.write(frame)
        data_len += written_bytes

    # Retrieve the accumulated data
    data = buffer.getvalue()
    # Close the buffer to free up memory
    buffer.close()
    return data, data_len
