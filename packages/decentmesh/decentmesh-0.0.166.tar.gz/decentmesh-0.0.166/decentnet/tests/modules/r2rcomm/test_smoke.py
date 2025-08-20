import asyncio
import socket
import unittest
from multiprocessing import Pipe
from unittest.mock import AsyncMock, patch

import cbor2

from decentnet.consensus.blockchain_params import BlockchainParams
from decentnet.consensus.cmd_enum import NetworkCmd
from decentnet.consensus.r2rcomm import BLOCK_COMMAND_PREFIX
from decentnet.modules.blockchain.block import Block
from decentnet.modules.tasks_base.r2r_comm import R2RComm
from decentnet.modules.tcp.socket_functions import recv_prefix


class TestR2RComm(unittest.TestCase):
    def setUp(self):
        # Create a multiprocessing pipe
        self.pipe_recv, self.pipe_send = Pipe(duplex=False)

        # Mock the relay object
        self.mock_relay = unittest.mock.MagicMock()
        self.mock_relay.alive = True
        self.mock_relay.beam_pipe_comm = {
            "test_process_uid": [self.pipe_recv, unittest.mock.MagicMock()]
        }
        self.mock_relay.received_beam_pub_key = "test_process_uid"
        self.mock_relay.beam.target_key = "target_key"

    @patch("decentnet.modules.tasks_base.r2r_comm.R2RComm.process_disconnect_block", new_callable=AsyncMock)
    def test_process_disconnect_block_invocation(self, mock_process_disconnect_block):
        # Arrange: Set up the mocked return value
        mock_process_disconnect_block.return_value = (
            "mock_serialized_block",
            Block(1, b"adasd", BlockchainParams.low_diff_argon, b""),
        )

        # Make relay.alive change to False after the first call
        def side_effect(*args, **kwargs):
            self.mock_relay.alive = False
            return "mock_serialized_block", Block(1, b"adasd", BlockchainParams.low_diff_argon, b"")

        mock_process_disconnect_block.side_effect = side_effect

        # Prepare data to send to the pipe
        disconnect_data = {
            "cmd": NetworkCmd.DISCONNECT_EDGE.value,
            "d": "target_key",
        }
        self.pipe_send.send(BLOCK_COMMAND_PREFIX + cbor2.dumps(disconnect_data))

        # Act: Initialize R2RComm
        R2RComm(self.mock_relay)

        # Assert: Check if process_disconnect_block was invoked
        mock_process_disconnect_block.assert_called_once_with(self.mock_relay, disconnect_data)

        # Assert: Verify that relay.alive is now False
        self.assertFalse(self.mock_relay.alive)


class TestRecvPrefix(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        """Setup a pair of connected sockets for testing."""
        self.server_sock, self.client_sock = socket.socketpair()
        self.server_sock.setblocking(False)  # Set to non-blocking for async reads
        self.client_sock.setblocking(False)

    async def asyncTearDown(self):
        """Clean up sockets."""
        self.server_sock.close()
        self.client_sock.close()

    async def test_recv_prefix(self):
        """Test that recv_prefix correctly receives the expected number of bytes."""
        prefix_data = b"\x00\x10"  # Example 2-byte prefix (16 in decimal)
        self.client_sock.sendall(prefix_data)

        # Run recv_prefix and verify the received data
        received_view = await recv_prefix(self.server_sock, len(prefix_data))
        self.assertEqual(received_view.tobytes(), prefix_data)

    async def test_recv_prefix_incomplete_data(self):
        """Test that recv_prefix raises ConnectionError if the socket closes early."""
        partial_data = b"\x00"  # Only 1 byte sent instead of 2
        self.client_sock.sendall(partial_data)
        await asyncio.sleep(0.1)  # Ensure send is processed
        self.client_sock.close()  # Simulate early close

        with self.assertRaises(ConnectionError):
            await recv_prefix(self.server_sock, 2)

    async def test_recv_prefix_zero_length(self):
        """Test that recv_prefix correctly returns an empty memoryview for zero-length input."""
        received_view = await recv_prefix(self.server_sock, 0)
        self.assertEqual(len(received_view), 0)


if __name__ == "__main__":
    unittest.main()
