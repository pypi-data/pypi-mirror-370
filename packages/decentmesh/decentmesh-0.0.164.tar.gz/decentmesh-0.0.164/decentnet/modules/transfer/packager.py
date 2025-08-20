import logging
from typing import Optional

import cbor2
from nacl.signing import SigningKey

from decentnet.consensus.blockchain_params import BROADCAST_PROPAGATION_TTL
from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.consensus.cmd_enum import NetworkCmd
from decentnet.consensus.dev_constants import (BLOCK_ERROR_DATA_LOG_LEN,
                                               RUN_IN_DEBUG)
from decentnet.modules.blockchain.block import Block
from decentnet.modules.convert.byte_to_base64_utils import bytes_to_base64
from decentnet.modules.cryptography.asymmetric import AsymCrypt
from decentnet.modules.key_util.key_manager import KeyManager
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.serializer.serializer import Serializer

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class Packager:
    @classmethod
    def genesis_package(cls, owner_key_id: int, receiver_key_pub_key: str,
                        block: Block):
        raise NotImplementedError()

    @classmethod
    def check_verified(cls, data: dict, verified: bool):
        """
        If verified is False, this will raise an exception with log
        :param data: Data of block for logging
        :param verified:
        """
        if not verified:
            logger.error(f"Invalid signature, failed to verify data: {data}")
            raise Exception("Invalid signature")

    @classmethod
    async def pack(cls, owner_key_id: int, block: Block,
                   target_pub_key: Optional[str], skip_sign=False) -> bytes:
        o_priv_key, o_pub_key = await KeyManager.retrieve_ssh_key_pair_from_db(owner_key_id)
        block_bytes = await block.to_bytes()

        if not skip_sign:
            signature = await cls.sign_block(owner_key_id, block_bytes)
        else:
            logger.debug("Skipping signing")
            signature = b""

        data = Serializer.serialize_data(
            o_pub_key, signature,
            block_bytes, target_pub_key)

        if RUN_IN_DEBUG:
            loaded_data = cbor2.loads(data)
            truncated_data = bytes_to_base64(data[:BLOCK_ERROR_DATA_LOG_LEN]) + "..." if len(
                data) > BLOCK_ERROR_DATA_LOG_LEN else loaded_data
            logger.debug("Packed data into %s" % truncated_data)

        return data

    @classmethod
    async def sign_block(cls, owner_key_id: int, block_bytes: bytes):
        o_priv_key, _ = await KeyManager.retrieve_ssh_key_pair_from_db(owner_key_id)
        block_bytes = block_bytes
        return AsymCrypt.sign_message(private_key=o_priv_key, data=block_bytes)

    @classmethod
    async def add_cmd(cls, unpacked_request: dict, owner_key_id: int, cmd: int) -> dict:
        """
        Adding cmd key to dict
        :param unpacked_request:
        :param owner_key_id:
        :param cmd: This is an int from CMD enum
        :return: Data with added cmd in dictionary
        """
        cpy_unpacked = dict(unpacked_request)
        o_priv_key, o_pub_key = await KeyManager.retrieve_ssh_key_pair_from_db(owner_key_id)
        cmd_bytes = cmd.to_bytes(2, byteorder=ENDIAN_TYPE, signed=False)
        signature = AsymCrypt.sign_message(private_key=o_priv_key, data=cmd_bytes)

        if cmd in (NetworkCmd.BROADCAST.value, NetworkCmd.DISCONNECT_EDGE.value):
            cpy_unpacked["ttl"] = BROADCAST_PROPAGATION_TTL

        cpy_unpacked["cmd"] = cmd
        cpy_unpacked["csig"] = signature
        cpy_unpacked["cpub"] = o_pub_key
        logger.debug("Added cmd and raw supporting values to packed result: %s" % cpy_unpacked)
        return cpy_unpacked

    @classmethod
    def unpack(cls, serialized_data: bytes, skip_key_verify: bool = False) -> (
            tuple)[bool, dict, Optional[bool]]:
        """
        Unpacks and verifies block
        :param skip_key_verify:
        :param serialized_data:
        :return: verified and data

        keys:
        "pub"
        "sig"
        "data"
        "target"
        """
        data = Serializer.deserialize_data(serialized_data)
        decoded_pub_key = AsymCrypt.verifying_key_from_string(data["pub"])
        # skip signature verify if encryption is enabled
        if not skip_key_verify:
            verified = AsymCrypt.verify_signature(
                public_key=decoded_pub_key,
                data=data["data"], signature=data["sig"])
        else:
            verified = True
            logger.debug("Skipping verify")

        if data.get("cmd", None) is not None:
            decoded_cpub_key = AsymCrypt.verifying_key_from_string(data["cpub"])
            verified_csig = Packager.verify_csig(data, decoded_cpub_key)
        else:
            verified_csig = None
        return verified, data, verified_csig

    @classmethod
    def verify_csig(cls, data, decoded_cpub_key):
        return AsymCrypt.verify_signature(
            public_key=decoded_cpub_key,
            data=data["cmd"].to_bytes(2, byteorder=ENDIAN_TYPE, signed=False),
            signature=data["csig"])

    @classmethod
    def sign_dict_data(cls, private_key: SigningKey, attribute: str, data: dict):
        """
        This will add signature to data attribute
        :param private_key:
        :param attribute:
        :param data:
        """
        signature = AsymCrypt.sign_message(private_key, data[attribute].encode("ascii"))
        data["sig"] = signature
        return data

    @classmethod
    def verify_dict_data(cls, public_key: str, attribute: str, data: dict):
        """
        Verifies data from a key in dict
        :param public_key:
        :param attribute:
        :param data:
        :return:
        """
        pub_key_raw = AsymCrypt.public_key_from_base64(public_key, False)
        return AsymCrypt.verify_signature(public_key=pub_key_raw, signature=data["sig"],
                                          data=data[attribute].encode("ascii"))
