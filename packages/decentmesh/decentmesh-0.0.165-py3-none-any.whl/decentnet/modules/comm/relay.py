import asyncio
import logging
import time
from datetime import datetime, UTC
from multiprocessing import Pipe
from typing import Any, Callable, Coroutine

import cbor2
import networkx as nx
from networkx import NetworkXNoPath, NodeNotFound
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from decentnet.consensus.blockchain_params import \
    SKIP_SIGNATURE_VERIFICATION_DEPTH, BlockchainParams
from decentnet.consensus.cmd_enum import NetworkCmd
from decentnet.consensus.dev_constants import METRICS, RUN_IN_DEBUG
from decentnet.consensus.relay_config import (RELAY_DEFAULT_ENCRYPTION_KEY_ID,
                                              RELAY_DEFAULT_SIGNING_KEY_ID,
                                              RELAY_FREQUENCY_DB_ALIVE_UPDATE)
from decentnet.consensus.routing_params import (DEFAULT_CAPACITY,
                                                MAX_ROUTE_LENGTH)
from .block_assembly import sign_block, assemble_disconnect_data
from ..blockchain.block import Block
from ..comm.beam import Beam
from ..comm.db_funcs import get_alive_beams
from ..cryptography.asymmetric import AsymCrypt
from ..db.base import session_scope
from ..db.constants import USING_ASYNC_DB
from ..db.models import AliveBeam, NodeInfoTable, Mail
from ..forwarding.flow_net import FlowNetwork
from ..internal_processing.blocks import ProcessingBlock
from ..key_util.key_manager import KeyManager
from ..logger.log import setup_logger
from ...consensus.r2rcomm import BLOCK_COMMAND_PREFIX

if METRICS:
    from ..monitoring.metric_server import ping, send_metric

from ..serializer.serializer import Serializer
from ..tasks_base.publisher import ClientBlockPublisher
from ..tcp.socket_functions import recv_all
from ..timer.relay_counter import RelayCounter
from ..timer.timer import Timer
from ..transfer.packager import Packager

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)

AsyncCallbackType = Callable[[str, str], Coroutine[Any, Any, Any]]


class Relay:

    def __init__(self, client_socket, beam_pipe_comm: dict, beam_msg_queue: dict,
                 callback: AsyncCallbackType | None = None,
                 beam: Beam | None = None):
        """
        Creates a passive relay that will listen on socket and relay incoming beams
        :param client_socket:
        :param beam_pipe_comm: Dict for beam synchronization
        :param beam_msg_queue: Dict for beam message queue
        :param callback:
        """
        ClientBlockPublisher(beam_msg_queue)
        self.skip_verification = False
        global RELAY_PROCESS_INSTANCE
        RELAY_PROCESS_INSTANCE = self

        self.do_metrics = asyncio.run(ping()) if METRICS else False
        if self.do_metrics:
            logger.debug("Metrics will be collected.. OK")
        else:
            logger.debug("Metrics in Relay will not be collected.. FAIL")

        self.relay_pub_key_bytes = None
        self.alive = True
        self.beam_pipe_comm = beam_pipe_comm
        self.received_beam_pub_key = None
        self.socket = client_socket
        self.client_ip = client_socket.getpeername()
        self.__callback = callback
        self.public_key_id = RELAY_DEFAULT_SIGNING_KEY_ID
        self.public_key_enc_id = RELAY_DEFAULT_ENCRYPTION_KEY_ID

        logger.debug(f"Initial Connection {self.client_ip}")
        self.local_port = self.client_ip[1]

        logger.info("Waiting for genesis block from new sender...")

        try:
            request = asyncio.run(recv_all(self.socket, self.client_ip[0], self.local_port))[0]
        except (ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, OSError):
            request = None

        if not request:
            raise ConnectionError

        self.network = FlowNetwork()

        verified, unpacked_request, verified_csig = Packager.unpack(request)
        Packager.check_verified(unpacked_request, verified)

        result = asyncio.run(self.execute_network_cmd_n_init_relay_key_bytes(unpacked_request, verified_csig))
        if result:
            return

        block = Block.from_bytes(unpacked_request["data"])  # Difficulty is checked when adding to blockchain

        self.received_beam_pub_key = pub_key = unpacked_request[
            "pub"]  # Key, which is received from unknown entity
        self.target_key = target_key = unpacked_request["target"]  # Key of mine or next destination

        self.init_pipes(beam_msg_queue, pub_key, target_key)

        if not beam:
            # Create a pipe for a relay beam communication between processes
            beam_pipe_comm[pub_key] = Pipe()

            self.beam = Beam(self.public_key_id, self.public_key_enc_id, target_key, self.do_metrics)
            # This is for each process to be able to get its relay address which is Relay public ckey
            global RELAY_PUB_KEY
            RELAY_PUB_KEY = pub_key

            self.beam.connect_using_socket(client_socket)
            asyncio.run(self.beam.initialize_incoming_transmission(block))
        else:
            self.beam = beam

        self.beam.lock()

        asyncio.run(self.complete_init_steps(block, pub_key, request, target_key, unpacked_request))

    async def execute_network_cmd_n_init_relay_key_bytes(self, unpacked_request, verified_csig):
        if verified_csig is not None:
            await self.execute_network_cmd(unpacked_request, verified_csig)
            return True  # Indicate that the function exited early

        _, self.relay_pub_key_bytes = await KeyManager.retrieve_ssh_key_pair_from_db(self.public_key_id)
        return False  # Indicate that the function continued normally

    async def send_all_undelivered_mail(self, target_key: str):
        async def __prepare_block_for_publish():
            next_block = self.beam.comm_bc.template_next_block(mail.block,
                                                               BlockchainParams.low_diff_argon)
            packed_data = await Packager.pack(self.public_key_id, next_block, target_key)
            verified, data, _ = Packager.unpack(packed_data)
            _data = await Packager.add_cmd(data, owner_key_id=self.public_key_id,
                                           cmd=NetworkCmd.REDELIVER_ON_CONNECT.value)
            serialized = Serializer.serialize_data(_data["pub"],
                                                   _data["sig"],
                                                   _data["data"],
                                                   _data["target"],
                                                   _data["cmd"],
                                                   _data["csig"],
                                                   _data["cpub"])
            return serialized

        send_pipe = self.beam_pipe_comm.get(target_key)
        if not send_pipe:
            return

        if USING_ASYNC_DB:
            async with session_scope() as session:
                await self._delete_expired_mail()
                result = await session.execute(
                    select(Mail).where(Mail.target == target_key)
                )
                mails = result.scalars().all()
                logger.debug(f"Will send {len(mails)} undelivered blocks from mailbox to {target_key}")

                for mail in mails:
                    await session.delete(mail)
                    serialized_broadcast = await __prepare_block_for_publish()
                    await ClientBlockPublisher.publish_message(target_key, serialized_broadcast)
        else:
            with session_scope() as session:
                await self._delete_expired_mail()
                result = session.execute(
                    select(Mail).where(Mail.target == target_key)
                )
                mails = result.scalars().all()
                logger.debug(f"Will send {len(mails)} undelivered blocks from mailbox to {target_key}")

                for mail in mails:
                    session.delete(mail)
                    serialized_broadcast = await __prepare_block_for_publish()
                    await ClientBlockPublisher.publish_message(target_key, serialized_broadcast)

    async def complete_init_steps(self, block: Block, pub_key: str, request: bytes, target_key: str,
                                  unpacked_request: dict):
        _, o_pub_key = await KeyManager.retrieve_ssh_key_pair_from_db(self.public_key_id)
        signing_pub_key = AsymCrypt.verifying_key_to_string(o_pub_key)
        await self.network.add_edge(signing_pub_key,
                                    pub_key, DEFAULT_CAPACITY)

        # TODO: look for undelivered mail

        if target_key != "NOT_KNOWN":
            await self.record_alive_beam(target_key, True)
            await self.send_all_undelivered_mail(pub_key)
            await self.relay_message_by_one(block, unpacked_request, request)

        # await self.network.add_edge(target_key, pub_key, DEFAULT_CAPACITY)
        if block.index == 0:
            logger.info(f"Adding connected Beacon {pub_key}")
            await self.save_beacon(pub_key)

            asyncio.create_task(
                self.broadcast_connected(block, pub_key, unpacked_request),
                name=f"Broadcasting of {pub_key}"
            )
        else:
            logger.info(f"Updating beacon connection {pub_key}")
            await self.update_beacon_connection(pub_key)
            await self.network.add_edge(pub_key,
                                        KeyManager.key_to_base64(target_key), None)
        if not self.beam.alive:
            self.beam.close()
            logger.warning("INVALID BLOCK, Closed connection")
        else:
            await self.beam.save_new_pub_key(pub_key, False, "New Beacon")

    @classmethod
    async def record_alive_beam(cls, pub_key: str, ready: bool):
        if USING_ASYNC_DB:
            async with session_scope() as session:
                alive_beam = (await session.execute(
                    select(AliveBeam).where(AliveBeam.pub_key == pub_key))).scalar_one_or_none()
                if alive_beam:
                    alive_beam.ready = ready
                else:
                    ab = AliveBeam(pub_key=pub_key, ready=ready)
                    session.add(ab)
        else:
            with session_scope() as session:
                alive_beam = (await session.execute(
                    select(AliveBeam).where(AliveBeam.pub_key == pub_key))).scalar_one_or_none()
                if alive_beam:
                    alive_beam.ready = ready
                else:
                    ab = AliveBeam(pub_key=pub_key, ready=ready)
                    session.add(ab)

    @classmethod
    def init_pipes(cls, beam_msg_queue, pub_key, target_key):
        if beam_msg_queue.get(pub_key, None) is None:
            beam_msg_queue[pub_key] = Pipe()
        if beam_msg_queue.get(target_key, None) is None:
            beam_msg_queue[target_key] = Pipe()

    @classmethod
    async def _add_block_to_mailbox(cls, serialized_block: bytes, target=None):
        if USING_ASYNC_DB:
            async with session_scope() as session:
                await cls._delete_expired_mail()
                session.add(Mail(block=serialized_block, target=target))
        else:
            with session_scope() as session:
                await cls._delete_expired_mail()
                session.add(Mail(block=serialized_block, target=target))

    @classmethod
    async def _delete_expired_mail(cls):
        now = datetime.now(UTC)
        if USING_ASYNC_DB:
            async with session_scope() as session:
                await session.execute(delete(Mail).where(Mail.expire_at < now))
        else:
            with session_scope() as session:
                session.execute(delete(Mail).where(Mail.expire_at < now))

    async def broadcast_connected(self, genesis_block: Block, connected_pub_key: str,
                                  unpacked_genesis: dict):
        """

        :param genesis_block:
        :param connected_pub_key: Pub key of the connected beacon needs to be base64
        :param unpacked_genesis: Unpacked genesis block in dict format
        """
        if genesis_block.index == 0:
            all_alive_beams = await get_alive_beams()

            _data = await Packager.add_cmd(
                unpacked_genesis, self.public_key_id, NetworkCmd.BROADCAST.value
            )
            ttl = _data.get("ttl", 0)
            logger.debug(
                f"Broadcasting connected beacon {connected_pub_key} to connected beams TTL {ttl}")
            block_with_signature = {
                "data": _data["data"],
                "sig": _data["sig"],
                "pub": _data["pub"]
            }
            # Template next connection block with broadcast block
            bb_data = cbor2.dumps(block_with_signature)
            broadcast_block = self.beam.conn_bc.template_next_block(bb_data, self.beam.conn_bc.difficulty)
            # broadcast_block.mine()
            if not await self.beam.conn_bc.insert(broadcast_block):
                raise Exception("Failed to insert broadcast block")
            broadcast_block_signature, broadcast_block_bytes = await sign_block(self.public_key_id,
                                                                                broadcast_block)
            serialized_broadcast = Serializer.serialize_data(
                self.relay_pub_key_bytes,
                broadcast_block_signature,
                broadcast_block_bytes,
                _data["target"],
                _data["cmd"],
                _data["csig"],
                _data["cpub"],
                ttl
            )

            await self._add_block_to_mailbox(broadcast_block_bytes)

            # Broadcasting connection to other beams

            if len(all_alive_beams):
                await self._broadcast_data(all_alive_beams, serialized_broadcast)
            else:
                logger.info(f"No one to broadcast to {connected_pub_key}")

    @classmethod
    async def _broadcast_data(cls, all_alive_beams: list, serialized_broadcast: bytes):
        for beam in all_alive_beams:
            # TODO: Skip broadcast to current
            logger.info(f"  broadcasting connection to {beam.pub_key}")
            await ClientBlockPublisher.publish_message(beam.pub_key, serialized_broadcast)

    async def update_beacon_connection(self, pub_key):
        await Relay.update_beacon(pub_key)
        await self.do_callback(pub_key, "ping")

    async def do_callback(self, pub_key: str, action: str):
        if self.__callback:
            await self.__callback(pub_key, action)

    async def do_relaying(self, t: Timer, relay_counter: RelayCounter):
        """
        This function provides a single relay of request from Relay loop
        :param t: Timer
        :param relay_counter: Counter of relays
        :return: Request size (if 0 connection closed)
        """
        self.alive = True
        logger.debug(
            f"Waiting for data from {self.received_beam_pub_key} for relaying on {self.client_ip}...")
        try:
            request, request_size = (await recv_all(self.socket, self.client_ip[0], self.local_port))
        except (ConnectionError, ConnectionResetError, ConnectionAbortedError,
                ConnectionRefusedError, OSError):
            return await self.erase_all_edge_connections()

        if not request:
            return await self.erase_all_edge_connections()

        if self.do_metrics:
            await send_metric("prom_data_received", request_size)
        logger.info(f"Relay Connection {self.socket.getpeername()}")
        try:
            await self.relay_request(request, t, relay_counter)
        except (cbor2.CBORDecodeError, cbor2.CBORDecodeValueError):
            logger.error(f"Unable to decode: {request}")
            logger.error("Suggesting disconnect")
            self.beam.unlock()
            return await self.erase_all_edge_connections()

        return request_size

    async def erase_all_edge_connections(self):
        all_alive_beams = await get_alive_beams()

        for beam in all_alive_beams:
            if beam.pub_key == self.beam.pub_key:
                logger.debug(f"Skipped broadcasting disconnect to {beam.pub_key}")
                continue
            serialized_broadcast = cbor2.dumps(await assemble_disconnect_data(self.public_key_id,
                                                                              self.beam.pub_key,
                                                                              self.received_beam_pub_key))
            if beam.pub_key in self.beam_pipe_comm.keys():
                # Send disconnect details to another process with the correct blockchain for block assembly
                self.beam_pipe_comm[beam.pub_key][1].send(BLOCK_COMMAND_PREFIX + serialized_broadcast)
            else:
                logger.warning(f"Missing {beam.pub_key} in pipe comm dict unable sending disconnect")

        self.alive = False
        await self.network.rm_edge(self.beam.pub_key, self.received_beam_pub_key)
        return 0

    async def _execute_network_cmd(self, data: dict, cmd_value: int):
        await self.do_callback(data["pub"], NetworkCmd(cmd_value).name)
        if cmd_value == NetworkCmd.BROADCAST.value:
            await ProcessingBlock.proces_broadcast_block(self.network, data)
            return await ProcessingBlock.decrease_ttl_broadcast_block(data)
        elif cmd_value == NetworkCmd.SYNCHRONIZE.value:
            block = Block.from_bytes(data["data"])
            await self.beam.conn_bc.insert(block)

            if not self.skip_verification:
                self.skip_verification = await self.check_if_verification_needed()
        elif cmd_value == NetworkCmd.DISCONNECT_EDGE.value:
            await ProcessingBlock.process_disconnect_block(self.network, data)
            return await ProcessingBlock.decrease_ttl_broadcast_block(data)
        return None

    async def check_if_verification_needed(self):
        res = len(self.beam.comm_bc) > SKIP_SIGNATURE_VERIFICATION_DEPTH
        if res:
            logger.debug(
                f"Beam {self.beam.pub_key} reached signature verification depth of "
                f"{SKIP_SIGNATURE_VERIFICATION_DEPTH}.. Skipping verification")
        return res

    async def execute_network_cmd(self, unpacked_request: dict, verified_csig: bool):
        Packager.check_verified(unpacked_request, verified_csig)
        cmd_value = unpacked_request["cmd"]

        if RUN_IN_DEBUG:
            logger.debug(f"Received verified cmd {NetworkCmd(cmd_value)}")

        changed_data = await self._execute_network_cmd(unpacked_request, cmd_value)

        if changed_data:
            await self.rebroadcast(changed_data)

    async def rebroadcast(self, changed_data):
        if RUN_IN_DEBUG:
            logger.debug(f"Rebroadcasting data TTL {changed_data.get("ttl")}")
        all_alive_beams = await get_alive_beams()
        serialized_broadcast = cbor2.dumps(changed_data)
        await self._broadcast_data(all_alive_beams, serialized_broadcast)

    async def relay_request(self, request: bytes, t: Timer, relay_counter: RelayCounter):
        """
        Relay specified request
        :param request: Request to relay
        :param t: Timer
        :param relay_counter: RelayCounter
        :return:
        """
        t.stop()

        verified, data, verified_csig = Packager.unpack(request, self.skip_verification)

        if not self.skip_verification:
            Packager.check_verified(data, verified)
            self.skip_verification = await self.check_if_verification_needed()

        if verified_csig is not None:
            await self.execute_network_cmd(data, verified_csig)
            return

        block = Block.from_bytes(data["data"])

        block.signature = data["sig"]
        beacon_pub_key = data["pub"]

        self.beam.comm_bc.difficulty = block.diff
        insert_res = await self.beam.comm_bc.insert(block)

        if relay_counter.count % RELAY_FREQUENCY_DB_ALIVE_UPDATE == 0:
            await self.update_beacon_connection(beacon_pub_key)
            relay_counter.reset()

        if not insert_res:
            logger.error(f"Failed to insert block, closing connection... {self.client_ip}")
            self.socket.close()
            self.alive = False

        if block.index > 0:
            try:
                await self.relay_message_by_one(block, data, request)
            except nx.NetworkXNoPath:
                logger.warning(f"No path between {self.received_beam_pub_key} => {data['target']}")

        block_process_time_timer = t.stop()
        if RUN_IN_DEBUG:
            logger.debug(f"Total block process time: {block_process_time_timer} ms")

        if self.do_metrics:
            await send_metric("prom_block_process_time", block_process_time_timer)

        relay_counter.count += 1

    async def relay_message_by_one(self, block: Block, data: dict, request: bytes):
        path = None
        send_pipe = None
        store_to_mailbox = False
        process_pub_key = None
        try:
            path, capacity = self.network.get_path(self.received_beam_pub_key, data["target"])
            path_len = len(path)
            if self.do_metrics:
                await send_metric("prom_block_path_len", path_len)

            if path_len == 1:
                logger.debug("Path too short")
                return
            if path and path_len > MAX_ROUTE_LENGTH:
                logger.info("Maximum path exceeded, connecting to closer relay for better latency...")
                # TODO: connect to the closer relay to make shorter path
            logger.debug(f"Found path {path} and capacity {capacity} for block {block.index}")
            if send_pipe := self.beam_pipe_comm.get(path[-1], False):
                process_pub_key = path[-1]
            elif send_pipe := self.beam_pipe_comm.get(path[1], False):
                process_pub_key = path[1]
            else:
                store_to_mailbox = True
                if len(path):
                    process_pub_key = path[-1]
        except NodeNotFound:
            logger.warning(f"Node {data['target']} not found")
            store_to_mailbox = True
        except NetworkXNoPath:
            logger.warning(f"Path to {data['target']} not found")
            store_to_mailbox = True

        if store_to_mailbox:
            await self._add_block_to_mailbox(data["data"], process_pub_key)
            logger.debug(f"Added block to mailbox for {process_pub_key} and quit")
            return

        if RUN_IN_DEBUG:
            logger.debug(
                f"Publishing from {self.received_beam_pub_key} message to {process_pub_key} on path {path}")

        if not send_pipe:
            logger.warning(f"No pipe to send message to {process_pub_key}")
            return

        # Syncing inter relay blockchain
        send_pipe[1].send(data["data"])

        await ClientBlockPublisher.publish_message(process_pub_key, request)

    @classmethod
    async def update_beacon(cls, pub_key: str):
        if USING_ASYNC_DB:
            async with session_scope() as session:
                # Perform an asynchronous query to get the beacon
                result = await session.execute(
                    select(NodeInfoTable).where(NodeInfoTable.pub_key == pub_key)
                )
                beacon = result.scalar_one_or_none()

                if beacon:
                    beacon.last_ping = time.time()
        else:
            with session_scope() as session:
                # Perform a synchronous query to get the beacon
                result = session.execute(
                    select(NodeInfoTable).where(NodeInfoTable.pub_key == pub_key)
                )
                beacon = result.scalar_one_or_none()

                if beacon:
                    beacon.last_ping = time.time()

    async def disconnect_beacon(self, port: int, pub_key: str):
        # Call the disconnect callback asynchronously
        if USING_ASYNC_DB:
            # Call the disconnect callback asynchronously
            await self.do_callback(pub_key, "disconnect")

            async with session_scope() as session:
                # Perform an asynchronous query to find the record to delete
                result = await session.execute(
                    select(NodeInfoTable).where(
                        (NodeInfoTable.port == port) & (NodeInfoTable.pub_key == pub_key)
                    )
                )
                record_to_delete = result.scalar_one_or_none()

                if record_to_delete:
                    await session.delete(record_to_delete)
        else:
            # Call the disconnect callback synchronously
            await self.do_callback(pub_key, "disconnect")

            with session_scope() as session:
                # Perform a synchronous query to find the record to delete
                result = session.execute(
                    select(NodeInfoTable).where(
                        (NodeInfoTable.port == port) & (NodeInfoTable.pub_key == pub_key)
                    )
                )
                record_to_delete = result.scalar_one_or_none()

                if record_to_delete:
                    session.delete(record_to_delete)

    async def save_beacon(self, pub_key: str):
        # Define a helper function to perform the database operations
        def add_beacon_to_session():
            client_ip = self.client_ip
            bdb = NodeInfoTable(
                ipv4=client_ip[0],
                port=client_ip[1],
                pub_key=pub_key,
            )
            session.add(bdb)

        # Define a helper function to handle commit and update
        async def commit_or_update_beacon():
            try:
                # Commit the transaction
                if USING_ASYNC_DB:
                    await session.commit()
                else:
                    session.commit()
            except IntegrityError:
                logger.debug(f"Updating connected node {self.client_ip[0]}:{self.client_ip[1]}")
                if USING_ASYNC_DB:
                    await session.rollback()
                    await Relay.update_beacon(pub_key)
                else:
                    session.rollback()
                    await Relay.update_beacon(pub_key)

        # Perform the callback
        if USING_ASYNC_DB:
            await self.do_callback(pub_key, "connect")

            async with session_scope() as session:
                add_beacon_to_session()
                await commit_or_update_beacon()
        else:
            await self.do_callback(pub_key, "connect")

            with session_scope() as session:
                add_beacon_to_session()
                await commit_or_update_beacon()


RELAY_PUB_KEY: str | None = None
RELAY_PROCESS_INSTANCE: Relay | None = None
