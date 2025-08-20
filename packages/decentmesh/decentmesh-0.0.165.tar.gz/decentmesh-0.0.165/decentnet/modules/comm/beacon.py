import asyncio
import logging
from socket import socket
from threading import Thread
from typing import Optional

from decentnet.consensus.dev_constants import METRICS, RUN_IN_DEBUG
from ..comm.beam import Beam
from ..comm.relay import Relay
from ..cryptography.asymmetric import AsymCrypt
from ..key_util.key_manager import KeyManager
from ..logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class Beacon:
    def __init__(self, ip: Optional[str], port: Optional[int], pub_key_id: int, ipv: Optional[int] = 4,
                 client_socket: Optional[socket] = None, do_metric: bool = METRICS):
        self.ip = ip
        self.port = port
        self.ipv = ipv
        self.pub_key = None
        self.pub_key_id = pub_key_id
        self.do_metric = do_metric

        _, o_pub_key = asyncio.run(KeyManager.retrieve_ssh_key_pair_from_db(pub_key_id))
        try:
            self.pub_key = AsymCrypt.verifying_key_to_string(o_pub_key)
        except AttributeError as ex:
            logger.fatal(f"Invalid verifying key {ex}")
            exit(1)

        self.client_socket = client_socket

    def create_beam(self, target: str, pub_key_enc_id: int, loopback=False):
        """
        Creates a beam to the beacon,
         you can image it like a graph-edge

         Warning: Currently is unsupported to create multiple beams to one relay because of internal relay logic

        :param loopback: Will init relay on the same socket and beam for relaying
        :param pub_key_enc_id: Public key for encryption id owned in a DB
        :param target: public key in base64 encoded string
        :return:
        """
        beam = Beam(pub_key_id=self.pub_key_id, pub_key_enc_id=pub_key_enc_id,
                    target_key=target, do_metrics=self.do_metric)
        ip_port = (self.ip, self.port, self.ipv)
        if self.ip is None or self.port is None:
            beam.connect_using_socket(self.client_socket)
        else:
            beam.connect_using_address(ip_port)
        beam_pipe_comm = dict()
        beam_msg_queue = dict()

        if beam.client:
            asyncio.run(beam.initialize_outgoing_transmission())
            if loopback:
                try:
                    Thread(target=lambda: Relay(beam.client.socket, beam_pipe_comm, beam_msg_queue,
                                                beam=beam),
                           daemon=True,
                           name=f"Relay thread for {beam.client.socket.getpeername()}").start()
                except ConnectionError:
                    logger.warning("Beacon disconnected from relay forcefully")
                    return None

            return beam
        else:
            return None
