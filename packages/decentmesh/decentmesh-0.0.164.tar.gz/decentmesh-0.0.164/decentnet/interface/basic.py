import asyncio
import logging
import time
from typing import Optional, Tuple

import cbor2
from cbor2 import CBORError

from decentnet.consensus.beam2beam import HANDSHAKE_MSG
from decentnet.consensus.blockchain_params import BlockchainParams
from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.interface_constants import DEFAULT_ACK_MSG_SIGN
from decentnet.consensus.net_constants import SEED_NODES_IPV4, SEED_NODES_IPV6
from decentnet.modules.comm.beacon import Beacon
from decentnet.modules.comm.beam import Beam
from decentnet.modules.cryptography.asymmetric import AsymCrypt
from decentnet.modules.forwarding.flow_net import FlowNetwork
from decentnet.modules.key_util.key_manager import KeyManager
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.pow.difficulty import Difficulty

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class BasicInterface:
    """
    The BasicInterface class provides methods to manage encrypted communication channels
    using beacon and beam objects. It supports initialization of sending and receiving
    channels, and handles encrypted data transmission over a decentralized network.
    """

    def __init__(self, target_key: str, target_enc_key: str):
        """
        Initialize the BasicInterface with target keys.

        Args:
            target_key (str): The public key of the target.
            target_enc_key (str): The encryption key of the target.
        """
        self.pub_key = None
        self._beam_receive = None
        self._beacon_receive = None
        self._beam_send = None
        self._beacon_send = None
        self._target_key = target_key
        self._target_enc_key = target_enc_key
        self._network = FlowNetwork()
        self.connected_relays = []

        self.encrypted_send = False
        self.encrypted_receive = False

    def init_sending(self, owner_sign_key_send_id: int, owner_enc_key_send_id: int):
        """
        Initialize the sending communication by connecting to a relay and setting up encryption.

        Args:
            owner_sign_key_send_id: The signing key ID for sending.
            owner_enc_key_send_id: The encryption key ID for sending.

        Returns:
            bool: True if encryption initialization is complete, False otherwise.
        """
        beacon_a, beam_a = self._single_relay_connect_outgoing(owner_sign_key_send_id, owner_enc_key_send_id)

        self._beacon_send = beacon_a
        self._beam_send = beam_a
        self.encrypted_send = self._beam_send.encryption_init_complete
        self.pub_key = self._beacon_send.pub_key

        return self._beam_send.encryption_init_complete

    def init_receiving(self, owner_sign_key_receive_id: int, owner_enc_key_receive_id: int):
        """
        Initialize the receiving communication by connecting to a relay and setting up encryption.

        Args:
            owner_sign_key_receive_id (int): The signing key ID for receiving.
            owner_enc_key_receive_id (int): The encryption key ID for receiving.

        Returns:
            bool: True if encryption initialization is complete, False otherwise.
        """
        beacon_b, beam_b = self._single_relay_connect_incoming(owner_sign_key_receive_id,
                                                               owner_enc_key_receive_id)

        self._beacon_receive = beacon_b
        self._beam_receive = beam_b
        self.encrypted_receive = self._beam_receive.encryption_init_complete

        return self._beam_receive.encryption_init_complete

    def _single_relay_connect_outgoing(self, owner_key_id: int, owner_enc_key_id: int) -> Tuple[
        Beacon, Beam]:
        """
        Connect to a single relay and initialize encryption for outgoing encryption.

        Args:
            owner_key_id (int): The owner's signing key ID.
            owner_enc_key_id (int): The owner's encryption key ID.

        Returns:
            Tuple[Beacon, Beam]: Connected Beacon and Beam objects.
        """
        beacon, beam = self.__auto_select_single_seed_node(owner_key_id, owner_enc_key_id)
        if not beacon:
            logger.critical("No connectable relay found.")
            exit(1)
        asyncio.run(self._init_out_encryption(beam))
        return beacon, beam

    def _single_relay_connect_incoming(self, owner_key_id: int, owner_enc_key_id: int) -> Tuple[
        Beacon, Beam]:
        """
        Connect to a single relay and initialize encryption for incoming connections.

        Args:
            owner_key_id (int): The owner's signing key ID.
            owner_enc_key_id (int): The owner's encryption key ID.

        Returns:
            Tuple[Beacon, Beam]: Connected Beacon and Beam objects.
        """
        beacon, beam = self.__auto_select_single_seed_node(owner_key_id, owner_enc_key_id)
        if not beacon:
            logger.critical("No connectable relay found.")
            exit(1)

        return beacon, beam

    def __auto_select_single_seed_node(self, owner_key_id: int, owner_enc_key_id: int):
        """
        Automatically select and connect to a seed node.

        Args:
            owner_key_id (int): The owner's signing key ID.
            owner_enc_key_id (int): The owner's encryption key ID.

        Returns:
            Tuple[Optional[Beacon], Optional[Beam]]: Connected Beacon and Beam objects if successful,
            otherwise (False, None).
        """
        seed_nodes = SEED_NODES_IPV4 + SEED_NODES_IPV6

        for node_v4 in seed_nodes:
            logger.debug(f"Trying to connect to {node_v4[0]}:{node_v4[1]}")
            node_v4_concat = "".join([str(n) for n in node_v4])
            if node_v4_concat + str(owner_key_id) not in self.connected_relays:
                try:
                    beacon = Beacon(node_v4[0], node_v4[1], owner_key_id, node_v4[2])
                    beam = beacon.create_beam(self._target_key, owner_enc_key_id, loopback=False)

                    if beam is None:
                        continue

                    _, o_pub_key = asyncio.run(KeyManager.retrieve_ssh_key_pair_from_db(beam.pub_key_id))
                    pub_key = AsymCrypt.verifying_key_to_string(o_pub_key)

                    asyncio.run(self._network.add_edge(pub_key,
                                                       beam.target_key, 10))

                    logger.info(f"[OK] Seed {node_v4[0]}:{node_v4[1]} connected!")
                    self.connected_relays.append(node_v4_concat + str(owner_key_id))
                    return beacon, beam
                except (ConnectionError, ConnectionResetError, ConnectionRefusedError,
                        ConnectionAbortedError, TimeoutError):
                    logger.debug(f"{node_v4[0]}:{node_v4[1]} failed to connect")
            else:
                logger.debug(
                    "This relay is not connectable with this key pair, as different beam is already connected.")
        return False, None

    async def _init_out_encryption(self, beam: Beam,
                                   difficulty: Difficulty = BlockchainParams.low_diff_argon):
        """
        Initialize encryption for a Beam.

        Args:
            beam (Beam): The Beam object to initialize encryption on.
            difficulty (Difficulty, optional): The difficulty level for the secure communication.
            Defaults to BlockchainParams.low_diff.

        Returns:
            bool: True if encryption is successfully initialized, False otherwise.
        """
        if beam.encryption_init_complete:
            logger.debug(f"Beam {beam.hash} already initialized encryption")
            return True

        beam.set_communication_difficulty(difficulty)
        logger.debug(f"Init b2b connection with {self._target_enc_key}")
        await beam.init_secure_b2b_connection(self._target_enc_key)

        logger.debug("Waiting for ack handshake")
        dec_data = await self._fetch_ack(beam)
        beam.encryption_init_complete = (dec_data["status"] == "OK")
        return beam.encryption_init_complete

    @classmethod
    async def _fetch_ack(cls, beam: Beam):
        """
        Fetch and decrypt the acknowledgement message from a Beam.

        Args:
            beam (Beam): The Beam object to fetch the acknowledgement from.

        Returns:
            dict: The decrypted acknowledgement data.
        """
        data = (await beam.fetch_message())[0].data
        try:
            dec_data = cbor2.loads(beam.encryptor_beacon.decrypt(bytes(data)))
        except ValueError as e:
            logger.debug(f"Failed to decrypt {bytes(data)}")
            raise e
        return dec_data

    async def send(self, data: bytes, difficulty: Difficulty = BlockchainParams.low_diff_argon,
                   require_ack: bool = False) -> Optional[bool]:
        """
        Send data over an initialized Beam with optional acknowledgement.

        Args:
            data (bytes): The data to be sent.
            difficulty (Difficulty, optional): The difficulty level for the secure communication.
            Defaults to BlockchainParams.low_diff.
            require_ack (bool, optional): Whether to wait for an acknowledgement.
            Defaults to False.

        Returns:
            Optional[bool]: Bool if acknowledgement is required and status is OK, otherwise None.
        """
        if self._beam_send is None or self._beacon_send is None:
            raise Exception("You need to initialize sending first!")

        self._beam_send.comm_bc.difficulty = difficulty

        e_data = data + DEFAULT_ACK_MSG_SIGN if require_ack else data

        await self._beam_send.send_communication_data(e_data)

        if require_ack:
            dec_data = await self._fetch_ack(self._beam_send)
            return dec_data["status"] == "OK"
        return None

    async def fetch(self, return_latency_ms: bool = False) -> dict | None | Tuple[dict, float]:
        """
        Fetch and decrypt data from the initialized receiving Beam.

        Returns:
            dict: The decrypted data as a dictionary.

        Raises:
            Exception: If receiving has not been initialized.
        """
        if self._beam_receive is None or self._beacon_receive is None:
            raise Exception("You need to initialize receiving first!")

        logger.info("Waiting for incoming beams")
        block = (await self._beam_receive.fetch_message(do_metrics=False))[0]
        data = self._beam_receive.encryptor_beacon.decrypt(bytes(block.data))
        if data[-4:] == b'ACK!':
            await self._beam_receive.send_communication_data(HANDSHAKE_MSG)
        try:
            if return_latency_ms:
                return cbor2.loads(data), (time.time_ns() - block.timestamp) // 1_000_000
            else:
                return cbor2.loads(data)
        except CBORError:
            return None
