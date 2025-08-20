import asyncio
import os
import socket
import threading
import unittest

from decentnet.modules.tcp.socket_functions import recv_all

# Constants for length prefix generation
BLOCK_PREFIX_LENGTH_BYTES = 4
ENDIAN_TYPE = "big"


@unittest.skipUnless(os.getenv("RUN_CONN_TESTS", "False").lower() in ("1", "true", "yes"),
                     "Skipping connection tests (RUN_CONN_TESTS not set to True)")
class TestRecvAllWithSockets(unittest.TestCase):
    HOST = "127.0.0.1"
    PORT = 0

    def setUp(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(1)
        self.server_host, self.server_port = self.server_socket.getsockname()

        # Shared variables for assertions in threads
        self.exception_flag = None

    def tearDown(self):
        self.server_socket.close()
        if self.exception_flag:
            raise self.exception_flag

    def start_server(self, server_handler):
        """Start the server with a specific handler."""
        self.server_thread = threading.Thread(target=server_handler, daemon=True)
        self.server_thread.start()

    def test_valid_data_transfer(self):
        # Create an event to signal that the server is ready.
        server_ready = threading.Event()

        def server_handler():
            try:
                # Signal that the server is ready to accept connections.
                server_ready.set()
                conn, _ = self.server_socket.accept()
                data, data_len = asyncio.run(recv_all(conn))
                self.assertEqual(data, b"Hello, world!")
                self.assertEqual(data_len, 13)
            except Exception as e:
                self.exception_flag = e
            finally:
                conn.close()

        self.start_server(server_handler)

        # Wait until the server is ready (or use a timeout as needed)
        if not server_ready.wait(timeout=5):
            self.fail("Server did not become ready in time")

        async def client_handler():
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_socket.connect((self.server_host, self.server_port))
                message = b"Hello, world!"
                data_len = len(message)
                length_prefix = int.to_bytes(data_len, BLOCK_PREFIX_LENGTH_BYTES, ENDIAN_TYPE, signed=False)
                client_socket.sendall(length_prefix + message)
            finally:
                client_socket.close()

        asyncio.run(client_handler())

    def test_incomplete_data(self):
        def server_handler():
            try:
                conn, _ = self.server_socket.accept()
                asyncio.run(recv_all(conn))
            except ConnectionError:
                pass  # Expected exception
            except Exception as e:
                self.exception_flag = e
            finally:
                conn.close()

        self.start_server(server_handler)

        async def client_handler():
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.server_host, self.server_port))
            try:
                message = b"Hello, world!"
                data_len = len(message)
                length_prefix = int.to_bytes(data_len, BLOCK_PREFIX_LENGTH_BYTES, ENDIAN_TYPE, signed=False)
                client_socket.sendall(length_prefix + message[:5])  # Send partial data
            finally:
                client_socket.close()

        asyncio.run(client_handler())

    def test_invalid_length_prefix(self):
        def server_handler():
            try:
                conn, _ = self.server_socket.accept()
                asyncio.run(recv_all(conn))
            except ValueError:
                pass  # Expected exception
            except Exception as e:
                self.exception_flag = e
            finally:
                conn.close()

        self.start_server(server_handler)

        async def client_handler():
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.server_host, self.server_port))
            try:
                client_socket.sendall(b"abcd")  # Invalid length prefix
            finally:
                client_socket.close()

        asyncio.run(client_handler())

    def test_oversized_payload(self):
        def server_handler():
            try:
                conn, _ = self.server_socket.accept()
                asyncio.run(recv_all(conn))
            except MemoryError:
                pass  # Expected exception
            except Exception as e:
                self.exception_flag = e
            finally:
                conn.close()

        self.start_server(server_handler)

        async def client_handler():
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.server_host, self.server_port))
            try:
                oversized_message = b"A" * (10 ** 7)  # 10 MB message
                data_len = len(oversized_message)
                length_prefix = int.to_bytes(data_len, BLOCK_PREFIX_LENGTH_BYTES, ENDIAN_TYPE, signed=False)
                client_socket.sendall(length_prefix + oversized_message)
            finally:
                client_socket.close()

        asyncio.run(client_handler())

    def test_unexpected_connection_close(self):
        def server_handler():
            try:
                conn, _ = self.server_socket.accept()
                asyncio.run(recv_all(conn))
            except ConnectionError:
                pass  # Expected exception
            except Exception as e:
                self.exception_flag = e
            finally:
                conn.close()

        self.start_server(server_handler)

        async def client_handler():
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.server_host, self.server_port))
            try:
                message = b"Hello, world!"
                data_len = len(message)
                length_prefix = int.to_bytes(data_len, BLOCK_PREFIX_LENGTH_BYTES, ENDIAN_TYPE, signed=False)
                client_socket.sendall(length_prefix)  # Send only prefix, then close
            finally:
                client_socket.close()

        asyncio.run(client_handler())


if __name__ == '__main__':
    unittest.main()
