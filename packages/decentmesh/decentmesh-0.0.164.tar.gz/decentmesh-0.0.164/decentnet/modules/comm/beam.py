import asyncio
import hashlib
import logging
import os
import threading
from datetime import datetime, timezone
from socket import socket
from typing import Tuple

import cbor2
import nacl
from _socket import gaierror
from networkx.exception import NodeNotFound

from decentnet.consensus.beam2beam import HANDSHAKE_MSG
from decentnet.consensus.beam_constants import (BEAM_AES_ENCRYPTION_KEY_SIZE,
                                                BEAM_HASH_SIZE, USED_ALGORITHM)
from decentnet.consensus.blockchain_params import (
    SKIP_SIGNATURE_VERIFICATION_DEPTH, BlockchainParams)
from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.consensus.cmd_enum import NetworkCmd
from decentnet.consensus.dev_constants import ENCRYPTION_DEBUG, RUN_IN_DEBUG, DEBUG_RELAY_USING
from decentnet.consensus.routing_params import DEFAULT_CAPACITY
from decentnet.modules.blockchain.block import Block
from decentnet.modules.blockchain.blockchain import Blockchain
from decentnet.modules.convert.byte_to_base64_utils import (base64_to_original,
                                                            bytes_to_base64)
from decentnet.modules.cryptography.asymmetric import AsymCrypt
from decentnet.modules.cryptography.symmetric_aes import AESCipher
from decentnet.modules.cryptography.symmetric_chacha import ChaChaCipher
from decentnet.modules.db.models import BeamTable
from decentnet.modules.forwarding.flow_net import FlowNetwork
from decentnet.modules.internal_processing.blocks import ProcessingBlock
from decentnet.modules.key_util.foreign_keys import KeyManagerForeign
from decentnet.modules.key_util.key_manager import KeyManager
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.pow.difficulty import Difficulty
from decentnet.modules.tcp.client import TCPClient
from decentnet.modules.transfer.packager import Packager

logger = logging.getLogger(__name__)
setup_logger(RUN_IN_DEBUG, logger)


class Beam:
    conn_bc: Blockchain  # This is a blockchain for connection to relay
    comm_bc: Blockchain | None  # Blockchain for Beacon2Beacon communication

    def __init__(self, pub_key_id: int, pub_key_enc_id: int, target_key: str, do_metrics=False):
        """
        Beam for sending data transmissions between relay and beacon, always ip_port or client_socket is required
        :param pub_key_id:
        :param target_key:
        """
        self.do_metric = do_metrics
        self.hash = None
        self._lock = False
        self.comm_bc = None
        self.beam_id = None
        self.alive = False
        self.connected = False
        self.pub_key = None  # Public key under which this beam is identified to others
        self.pub_key_id = pub_key_id
        self.skip_verification = False
        _, o_pub_key = asyncio.run(KeyManager.retrieve_ssh_key_pair_from_db(
            self.pub_key_id))

        _, o_pub_enc_key = asyncio.run(KeyManager.retrieve_ssh_key_pair_from_db(pub_key_enc_id,
                                                                                can_encrypt=True))
        self.pub_enc_key = AsymCrypt.encryption_key_to_base64(o_pub_enc_key)
        self.pub_key = AsymCrypt.verifying_key_to_string(o_pub_key)
        self.target_key = target_key
        if DEBUG_RELAY_USING:
            if self.target_key != "NOT_KNOWN":
                logger.debug(
                    f"Using identity {self.pub_key} to receive data from {self.target_key} on thread {threading.current_thread().name} PID: {os.getpid()}")
            else:
                logger.debug(
                    f"Using identity {self.pub_key} to receive data from new beacons on thread {threading.current_thread().name} PID: {os.getpid()}")
        self.encryptor_relay: None | AESCipher = None
        self.encryptor_beacon: None | AESCipher = None
        self.client = None
        self.flow_net = FlowNetwork()
        self.encryption_init_complete = False

    def connect_using_address(self, ip_port: tuple):
        """
        Connects to address using ip_port tuple
        :param ip_port:
        :return:
        """
        if ip_port:
            try:
                self.client = TCPClient(ip_port[0], ip_port[1], ip_type=ip_port[2])
                self.hash = Beam.create_beam_hash(self.client.port)
                return True
            except gaierror:
                logger.debug(f"Failed to resolve {ip_port}")
                return False
            except ConnectionRefusedError:
                # logger.debug(f"No connection to {ip_port}")
                return False
        return False

    def connect_using_socket(self, client_socket: socket):
        """
        Connects to socket using client_socket
        :param client_socket:
        :return:
        """
        logger.debug("Reusing socket for beam")
        self.client = TCPClient(client_socket=client_socket)
        self.hash = Beam.create_beam_hash(self.client.port)
        return True

    async def initialize_incoming_transmission(self, genesis_block: Block) -> bool:
        """
        Connects incoming transmission and sends handshake block with encryption rules
        :param genesis_block:
        """
        self.conn_bc = Blockchain(pub_key_for_encryption=None,
                                  beam_id=self.beam_id, name="Connection blockchain",
                                  do_metric=self.do_metric)
        # await self.conn_bc.finish_blockchain_init()
        self.conn_bc.difficulty.compression_type = genesis_block.diff.compression_type
        logger.debug("Connection incoming with genesis %s" % genesis_block)
        await self.__connect_incoming(genesis_block, self.target_key)
        await self.init_comm_blockchain(True)
        self._save()
        return self.connected

    async def initialize_outgoing_transmission(self) -> bool:
        """
        Initializes outgoing transmission
        :return:
        """
        self.conn_bc = Blockchain(BlockchainParams.default_genesis_msg,
                                  pub_key_for_encryption=self.pub_enc_key,
                                  beam_id=self.beam_id, name="Connection blockchain",
                                  do_metric=False)
        await self.conn_bc.finish_blockchain_init()
        logger.debug(f"Connecting outgoing from {self.target_key}")
        await self.__connect_outbound_connection(self.pub_key_id, self.target_key)

        await self.init_comm_blockchain(True)

        self._save()
        return self.connected

    async def init_comm_blockchain(self, insert: bool, do_metric: bool = None):
        """
        Initializes communication blockchain from genesis block of connection blockchain
        """
        logger.debug(
            f"Initiation of communication blockchain with pub_enc {self.conn_bc.pub_key_for_encryption}")
        self.comm_bc = Blockchain(pub_key_for_encryption=self.conn_bc.pub_key_for_encryption,
                                  beam_id=self.beam_id, name="Communication Blockchain",
                                  do_metric=self.do_metric if do_metric is None else do_metric)
        await self.comm_bc.finish_blockchain_init()
        self.comm_bc.difficulty.compression_type = self.conn_bc.difficulty.compression_type
        if insert:
            if not await self.comm_bc.insert(self.conn_bc.chain[0]):
                raise Exception(
                    "Failed to initialize communication blockchain, genesis block may be invalid")

    def lock(self):
        self._lock = True

    def unlock(self):
        self._lock = False

    async def __connect_outbound_connection(self, pub_key_id, target_key):
        self.alive = len(self.conn_bc) > 0
        logger.debug(
            f"Sending Genesis block of Connection and Communication BC -> \n{self.conn_bc.get_last()}")
        response_handshake = await self.send_block(pub_key_id, target_key,
                                                   self.conn_bc.get_last())

        if not response_handshake:
            logger.warning(f"Got empty response, target {target_key}")
            self.close()
            raise Exception(f"Got empty response, target {target_key}")

        logger.debug("Response from Relay %s" % response_handshake)
        block = Block.from_bytes(response_handshake["data"])

        if not await self.conn_bc.insert(block):
            raise Exception("Invalid handshake block")

        block_data = cbor2.loads(block.data)

        if block_data["data"] != "CONNECTED":
            logger.warning("Connection failed, perhaps bad block")
            logger.debug("Block data %s" % block_data)
            self.close()
            raise Exception(f"Connection failed, perhaps bad block {block}")
        else:
            if self.target_key is None:
                self.target_key = response_handshake["pub"]
            logger.debug(f"Received new pubkey {self.target_key}")

            try:
                await self.process_handshake_block(block_data, True)
            except KeyError as e:
                logger.fatal("Wrong handshake block")
                logger.debug("Block data %s" % block_data)
                raise Exception(f"Wrong handshake block error {e}")

            await self.save_new_pub_key(self.pub_key, False, "New Beacon")
        self.connected = self.alive and self.encryptor_beacon

    async def process_handshake_block(self, block_data: dict, relay: bool, send_ack=True):
        """
        Process handshake block and save encryptor to either
        encryptor_relay if relay is True or encryptor_beacon if relay is False
        :param send_ack:
        :param block_data:
        :param relay:
        :return:
        """
        # Command does not have to be verified, block data are signed
        if not isinstance(block_data, dict):
            logger.error(f"Block data must be a dict not {block_data}")
            raise TypeError("Block data must be a dict")

        if block_data["cmd"] == NetworkCmd.HANDSHAKE_ENCRYPTION.value:
            logger.debug(
                f"Received handshake block | Using {block_data['algo']}-{block_data['bits']}")
            encryption_algorithm = block_data["algo"]
            encryption_bits = block_data["bits"]
            encrypted_key = base64_to_original(block_data["key"])

            private_key_from_db = await KeyManager.get_private_key(self.pub_enc_key)
            # TODO: from relay keys
            try:
                data_enc_pwd = AsymCrypt.decrypt_message(
                    private_key_from_db,
                    encrypted_key)
            except nacl.exceptions.CryptoError as e:
                logger.fatal(f"Failed to decrypt handshake data from related public key {self.pub_enc_key}")
                raise e

            await self.set_encryptors(data_enc_pwd, encryption_algorithm, encryption_bits, relay)

            logger.debug(f"Connected to {self.pub_key}")
            logger.debug("Decrypted key successfully")
            if relay:
                logger.info(
                    f"Relay connection beam from {self.pub_key} => {self.target_key} has {encryption_algorithm}-{encryption_bits} enabled!")
            else:
                logger.info(
                    f"Direct path beam from {self.pub_key} => {self.target_key} has {encryption_algorithm}-{encryption_bits} enabled!")
            if send_ack:
                await self.send_ack_connect(self.pub_key, self.target_key)

            return encryption_algorithm, encryption_bits
        return None

    async def set_encryptors(self, data_enc_pwd: bytes, encryption_algorithm: str, encryption_bits: int,
                             relay: bool):
        if encryption_algorithm == "AES":
            cipher = AESCipher(data_enc_pwd, encryption_bits)
            if relay:
                self.encryptor_relay = cipher
            else:
                self.encryptor_beacon = cipher
        elif encryption_algorithm == "CC20":
            cipher = ChaChaCipher(data_enc_pwd, encryption_bits)
            if relay:
                self.encryptor_relay = cipher
            else:
                self.encryptor_beacon = cipher
        else:
            raise NotImplementedError(
                f"Not implemented encryptor {encryption_algorithm}")

    async def __connect_incoming(self, genesis_block: Block, target_key: str):
        self.alive = await self.conn_bc.insert(genesis_block)

        if not self.alive:
            logger.warning("Failed to insert genesis block, closing connection.")
            self.close()

        block_data = cbor2.loads(genesis_block.data)
        logger.debug("Received genesis block data: %s" % block_data)
        received_encryption_pub_key = block_data["enc_pub_key"]
        new_diff = Difficulty.from_bytes(block_data["new_diff"].encode("ascii"))
        self.conn_bc.difficulty = new_diff

        # TODO: handshake block should not be sent if target key is known, as the connection is not only for connection
        logger.debug(
            f"Setting new public encryption key for Connection blockchain {received_encryption_pub_key}")
        self.conn_bc.pub_key_for_encryption = received_encryption_pub_key

        logger.debug("Sending handshake block")
        handshake_block, pwd = Blockchain.create_handshake_encryption_block_raw(
            received_encryption_pub_key, algorithm=USED_ALGORITHM, additional_data="CONNECTED")

        logger.debug("Waiting for ack...")

        response = await self.send_connection_data(handshake_block, ack=True)

        await self.set_encryptors(pwd, USED_ALGORITHM, BEAM_AES_ENCRYPTION_KEY_SIZE, relay=True)

        if not response:
            logger.error("Response is empty")
            self.close()
            raise Exception("Response is empty")
        if Packager.verify_dict_data(response["pub"], "status", response):
            logger.debug("Verified ack message, finalized connection.")
            if self.target_key is None:
                self.target_key = response["pub"]
        else:
            self.connected = False
            logger.error(f"Failed to verify ack message from {response['pub']}")
            logger.debug(f"Ack message obtained {response}")
            self.close()
            raise Exception("Failed to verify ack message, maybe MITM attack ?")

        await self.save_new_pub_key(received_encryption_pub_key,
                                    description=f"Key from {target_key}",
                                    can_encrypt=True)
        self.connected = self.alive and self.encryptor_beacon
        logger.info("Connected with ACK verification.")
        logger.debug(f"Incoming connection alive? {self.connected}")

    async def send_block(self, pub_key_id, target_key, block: Block, request_ack=True) -> dict:
        """Send block with needed pack structure

        Verification is skipped if blockchain gets long as we use AES encryption after 2nd block
        """
        data = await Packager.pack(pub_key_id,
                                   block, target_key, self.skip_verification)
        logger.debug("Sending block %s, will wait for ack..." % block)
        response = await self.client.send_message(data, request_ack)
        return response

    @classmethod
    def create_beam_hash(cls, port: int):
        """
        Create a beam hash using blake2b to identity beams
        :return:
        """
        timestamp = datetime.now(timezone.utc)
        timestamp_str = timestamp.isoformat()

        # Hash the timestamp string using BLAKE2b
        return bytes_to_base64(hashlib.blake2b(timestamp_str.encode("ascii"),
                                               salt=port.to_bytes(2,
                                                                  byteorder=ENDIAN_TYPE,
                                                                  signed=False),
                                               digest_size=BEAM_HASH_SIZE).digest())

    async def save_new_pub_key(self, pub_key: str, can_encrypt: bool, description: str):
        await KeyManagerForeign.save_to_db(pub_key, description, can_encrypt,
                                           self.client.host, self.client.port)

    async def send_ack_connect(self, source_key: str, target_key: str):
        pk, pub = await KeyManager.retrieve_ssh_key_pair_from_db(self.pub_key_id)
        pub_key = AsymCrypt.verifying_key_to_string(pub)
        found = True
        try:
            _, _ = self.flow_net.get_path(source_key, target_key)
        except NodeNotFound:
            found = False
        msg = {"status": "CONNECTED" if self.alive else "CLOSED",
               "node_found": found,
               "pub": pub_key,
               }

        signed_data = Packager.sign_dict_data(pk, "status", msg)

        logger.debug("Sending ack connect message")
        await self.client.send_message(cbor2.dumps(signed_data),
                                       False)
        return True

    async def send_connection_data(self, data_raw: bytes, ack: bool = False) -> dict:
        """
        Sending connection data,
        typically used for communication with relay or internal decentmesh communication
        :param data_raw:
        :param ack:
        :return:
        """
        return await self.__send_data(data_raw, ack, self.conn_bc, encryptor=self.encryptor_relay)

    async def send_communication_data(self, data_raw: bytes, ack: bool = False) -> dict:
        """
        Sending communication data, is used for data transmission for user
        This data is automatically encrypted if encryptor is set
        :param data_raw:
        :param ack:
        :return:
        """
        logger.debug("Trying to send communication data %s B" % (len(data_raw)))
        if len(self.comm_bc) == 0:
            logger.debug("Inserted genesis block from connection blockchain as communication is outbound")
            await self.comm_bc.insert(self.conn_bc.chain[0])

        if self.encryptor_beacon is None:
            logger.warning("! Communication data are sent unencrypted !")

        return await self.__send_data(data_raw, ack, self.comm_bc, encryptor=self.encryptor_beacon)

    async def __send_data(self, data_raw: str | bytes, ack: bool, blockchain: Blockchain,
                          encryptor: AESCipher | ChaChaCipher | None) -> dict:
        """
        Send Data with use of specified blockchain
        :param ack: This ack is used only for internal decent connect communication do not use for communication
        :param data_raw:
        :param encryptor: If encryptor is passed, data will be encrypted
        :return:
        """

        if encryptor:
            encrypted_data = encryptor.encrypt(data_raw)
            if RUN_IN_DEBUG:
                logger.debug(f"Encrypted data to {encrypted_data} B")
            if ENCRYPTION_DEBUG:
                logger.debug(f"PWD {encryptor.password} {encryptor.salt}")
                logger.debug(f"Sending encrypted data {encrypted_data} {data_raw}")
        else:
            encrypted_data = None

        block = blockchain.template_next_block(encrypted_data if encrypted_data else data_raw,
                                               blockchain.difficulty)

        block.mine()

        if not await blockchain.insert(block):
            raise Exception(f"Failed to insert block {block}")
        packaged_data = await Packager.pack(self.pub_key_id, block, self.target_key,
                                            self.skip_verification if self.comm_bc else False)

        response = await self.client.send_message(packaged_data, ack=ack)
        logger.debug(f"Response from sending message {response}")
        return response

    def decrypt_block_data(self, block: Block) -> dict:
        return cbor2.loads(self.encryptor_relay.decrypt(block.data))

    async def fetch_message(self, do_metrics=None, listen_for_target_broadcast_block=False) -> Tuple[
        Block, dict, bytes | bytearray | str]:
        """
            Waits for and processes a serialized block message from a connected client.

            This method listens for an incoming message,
            deserializes it into a Block instance, and inserts it into an incoming blockchain.
            If no client connection exists, it raises an exception.
            It relies on Packager.unpack to process the specific message format and extract block data,
            while logging the received block for debugging.

               Returns:
                   Block: The Block instance deserialized from the received message.
                   dict: Unpacked original data in dict
                   bytes: Raw data

               Raises:
                   Exception: If no client connection is established prior to invocation.

               Side Effects:
                   - Reads a message from the network through the `client.receive_message` interface.
                   - Inserts the received block into the `blockchain`

               Note:
                   This method does validate the received block as it is inserting block.
        """
        if self._lock:
            raise Exception("You can not receive data from beam that is used by Relay!")

        if not self.client:
            raise Exception("No connection is established.")

        # Ignore broadcast blocks of other that got connected
        incoming_raw = await self.client.receive_message(decode=False)
        verified, incoming_data, verified_csig = Packager.unpack(incoming_raw, self.skip_verification)
        Packager.check_verified(incoming_data, verified)
        block = Block.from_bytes(incoming_data["data"])

        # WORKAROUND TODO: FIX
        if block.index == 0 and len(self.comm_bc) == 1:
            # Workaround if comm blockchain is initialized with improper genesis
            await self.init_comm_blockchain(False, do_metric=do_metrics)
            await self.comm_bc.insert(block)

            if not self.skip_verification:
                self.skip_verification = self.check_if_verification_skippable()

        cbor_loaded_data = cbor2.loads(block.data)
        if cbor_loaded_data == 0:
            if RUN_IN_DEBUG:
                logger.debug("Block data is not directly loadable, checking for commands")

            if self.encryptor_beacon and RUN_IN_DEBUG:
                logger.debug(f"Received encrypted block #{block.index}, passing data without loading...")
            elif incoming_data["cmd"] == NetworkCmd.REDELIVER_ON_CONNECT.value:
                real_block = Block.from_bytes(block.data)
                if listen_for_target_broadcast_block:
                    return real_block, incoming_data, incoming_raw
                else:
                    logger.debug(
                        "Received Redeliver block from Relay but silently skipping due to ignore flag...")
                    return await self.fetch_message(do_metrics=do_metrics)
            else:
                raise Exception(f"Failed to load block data {block}")

        if verified_csig is not None:  # Broadcast is faulty or handled incorrectly
            # Verifying command signature
            Packager.check_verified(incoming_data, verified_csig)
            logger.debug(
                f"Handling connection data {incoming_data['cpub']} {NetworkCmd(incoming_data['cmd']).name}")
            await self.handle_connection_data(incoming_data, block)
            return await self.fetch_message(do_metrics=do_metrics)
        elif block.index == 0:
            logger.debug(f"Received enc pub key genesis block from {incoming_data['pub']}")
            await self.save_new_pub_key(cbor_loaded_data["enc_pub_key"],
                                        description=f"Key from {incoming_data['pub']}",
                                        can_encrypt=True)
            if listen_for_target_broadcast_block and incoming_data["pub"] == self.target_key:
                logger.debug(
                    f"Received broadcast block from target {self.target_key}, target is ready to receive data!")
                return block, incoming_data, incoming_raw
            else:
                return await self.fetch_message(do_metrics=do_metrics)

        if incoming_data["pub"] == self.target_key and block.index < len(self.comm_bc):
            logger.debug(f"Obtained genesis block twice from target {self.target_key}")
            logger.debug(f"Current Genesis {self.comm_bc.chain[0]}")
            logger.debug(f"Received genesis {block}")

            return await self.fetch_message(do_metrics=do_metrics)

        if self.encryptor_beacon is None:
            logger.debug("Expecting handshake block, trying to process")
            await self.process_handshake_block(cbor_loaded_data, False, False)
            self.comm_bc.difficulty = block.diff
            await self.comm_bc.insert(
                block)  # Genesis block differs, need to get genesis block from sender maybe broadcast ?
            if not self.skip_verification:
                self.skip_verification = self.check_if_verification_skippable()
            await self.send_communication_data(cbor2.dumps(HANDSHAKE_MSG))
            logger.debug("Waiting for incoming traffic")
            return await self.fetch_message(do_metrics=do_metrics)

        logger.debug(f"Received block {block}")

        # TODO: add requesting difficulty to avoid spam
        self.comm_bc.difficulty = block.diff
        await self.comm_bc.insert(block)

        if not self.skip_verification:
            self.skip_verification = self.check_if_verification_skippable()

        return block, incoming_data, incoming_raw

    def check_if_verification_skippable(self):
        return len(self.comm_bc) > SKIP_SIGNATURE_VERIFICATION_DEPTH

    async def handle_connection_data(self, incoming_data: dict, incoming_block: Block):
        logger.debug(f"> Processing received connection block {incoming_data}")
        self.conn_bc.difficulty = incoming_block.diff
        await self.conn_bc.insert(incoming_block)

        if incoming_block.index == 0 and len(self.conn_bc) > 0:
            if (cmd := incoming_data.get("cmd", None)) and cmd == NetworkCmd.BROADCAST.value:
                await self.flow_net.add_edge(incoming_data["pub"], self.target_key,
                                             DEFAULT_CAPACITY)
                logger.debug("Adding edge from broadcast block")
            else:
                logger.debug(
                    f"Received connection block {incoming_block}, processing not implemented")
        if incoming_data["cmd"] == NetworkCmd.DISCONNECT_EDGE.value:
            await ProcessingBlock.process_disconnect_block(self.flow_net, incoming_data)

    def set_communication_difficulty(self, difficulty: Difficulty):
        self.comm_bc.difficulty = difficulty

    async def init_secure_b2b_connection(self, target_enc_key: str):
        """
        Init secure beacon to beacon connection over communication stream
        :param target_enc_key: Target encryption public key
        """
        block, data_enc_pwd = self.comm_bc.create_handshake_encryption_block_dict(
            target_enc_key)
        handshake_block_bytes = self.comm_bc.convert_handshake_block_dict_to_bytes(block)
        await self.send_communication_data(handshake_block_bytes, False)
        encryption_algorithm = block["algo"]
        encryption_bits = block["bits"]
        await self.set_encryptors(data_enc_pwd, encryption_algorithm, encryption_bits, False)

    def close(self):
        self.client.close()

    def _save(self):
        if self.comm_bc.save or self.conn_bc.save:
            asyncio.create_task(
                BeamTable.save(self, self.pub_key, self.target_key, self.conn_bc.id, self.comm_bc.id),
                name="SaveBeamTable"
            )
