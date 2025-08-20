import asyncio
import logging
import multiprocessing
import socket
from threading import Thread

import rich
from rich.panel import Panel

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.difficulty_ports_mapping import PORT_DIFFICULTY_CONFIG
from decentnet.consensus.net_constants import BLOCKED_IPV4, BLOCKED_IPV6
from decentnet.modules.comm.relay import Relay
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.req_queue.reques_queue import ReqQueue
from decentnet.modules.tasks_base.consumer import Consumer
from decentnet.modules.tasks_base.r2r_comm import R2RComm
from decentnet.modules.tcp.db_functions import \
    remove_alive_beam_from_db_w_pub_key
from decentnet.modules.tcp.socket_functions import set_sock_properties
from decentnet.modules.timer.relay_counter import RelayCounter
from decentnet.modules.timer.timer import Timer

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class TCPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        if ":" not in host:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
        else:
            self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            # Allow dual-stack (IPv4 + IPv6) connections
            self.server.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
            self.server.bind((self.host, self.port, 0, 0))

        self.clients = []

    @staticmethod
    def create_socket(host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock

    @staticmethod
    def handle_client(client_socket,
                      beam_pipe_comm: dict, beam_message_queue: dict):
        """
        Handle a client connection

        ! This function is run by separate process
        :param beam_message_queue: Beam multiprocess message queue
        :param client_socket:
        :param beam_pipe_comm:
        :return:
        """

        Thread(target=ReqQueue.do_requests, name="Request Queue", daemon=True).start()

        relay = None
        try:
            relay = Relay(client_socket, beam_pipe_comm, beam_message_queue)
        except ConnectionError:
            logger.debug("Beacon disconnected before providing genesis block.")
            return

        try:
            sock_name = client_socket.getsockname()
        except OSError as e:
            logger.error(e)
            logger.info("Socket was closed, unable to continue.")
            asyncio.run(relay.record_alive_beam(relay.target_key, False))
            return

        Thread(target=lambda: R2RComm(relay), name=f"R2R Communication {relay.target_key}",
               daemon=True).start()

        Thread(target=lambda: Consumer(relay, beam_message_queue),
               name=f"Consumer Runner {client_socket}", daemon=True).start()

        t = Timer()

        relay_counter = RelayCounter()

        while True:
            try:
                if not asyncio.run(relay.do_relaying(t, relay_counter)):
                    asyncio.run(
                        TCPServer.graceful_shutdown(beam_message_queue, beam_pipe_comm, relay, sock_name))
                    break
            except (ConnectionError, ConnectionResetError, ConnectionAbortedError,
                    ConnectionRefusedError):
                asyncio.run(TCPServer.graceful_shutdown(beam_message_queue, beam_pipe_comm, relay, sock_name))
                break

    @staticmethod
    async def graceful_shutdown(beam_message_queue, beam_pipe_comm, relay, sock_name):
        logger.info(
            f"Disconnected {sock_name[0]}:{relay.local_port}")  # TODO: Delete from connected
        await relay.disconnect_beacon(relay.local_port, relay.received_beam_pub_key)
        await remove_alive_beam_from_db_w_pub_key(relay.received_beam_pub_key)
        await relay.network.rm_edge(relay.beam.pub_key, relay.received_beam_pub_key)

        if relay.received_beam_pub_key:
            if beam_pipe_comm.get(relay.received_beam_pub_key):
                beam_pipe_comm[relay.received_beam_pub_key][0].close()
                beam_pipe_comm[relay.received_beam_pub_key][1].close()
            if beam_message_queue.get(relay.received_beam_pub_key):
                beam_message_queue[relay.received_beam_pub_key][0].close()
                beam_message_queue[relay.received_beam_pub_key][1].close()
            beam_message_queue.pop(relay.received_beam_pub_key, None)
            beam_pipe_comm.pop(relay.received_beam_pub_key, None)

    def run(self):
        diff_setting = PORT_DIFFICULTY_CONFIG[self.port]
        self.server.listen(diff_setting.max_hosts)
        logger.info(f"[*] Listening on {self.host}:{self.port}")
        welcome_string = (f"Started DecentMesh... OK\n"
                          f"Listening on {self.host}:{self.port}\n"
                          f"Listening for maximum hosts {diff_setting.max_hosts}\n"
                          f"Seed difficulty: {diff_setting.seed_difficulty}\n"
                          f"Low difficulty: {diff_setting.low_diff_argon}")
        rich.print(Panel(welcome_string, title="DecentMesh Status"))
        manager = multiprocessing.Manager()
        beam_pipe_comm = manager.dict()
        beams_message_queue = manager.dict()

        while True:
            client_socket, client_address = self.server.accept()

            set_sock_properties(client_socket)

            if client_address in (BLOCKED_IPV4 + BLOCKED_IPV6):
                logger.debug(f"Blocked {client_address}, found in blacklist.")
                client_socket.close()
                continue

            logger.info(
                f"[*] Accepted connection from {client_address[0]}:{client_address[1]}")
            client_process = multiprocessing.Process(target=TCPServer.handle_client,
                                                     name=f"Handling client {client_address}",
                                                     args=(
                                                         client_socket,
                                                         beam_pipe_comm,
                                                         beams_message_queue
                                                     )
                                                     , daemon=True)
            client_process.start()

    def close(self):
        for client_socket in self.clients:
            client_socket.close()
        self.server.close()
