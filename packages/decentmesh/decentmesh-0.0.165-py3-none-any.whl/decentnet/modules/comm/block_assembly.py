import logging
from typing import Tuple

import cbor2

from decentnet.consensus.cmd_enum import NetworkCmd
from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.blockchain.block import Block
from decentnet.modules.cryptography.asymmetric import AsymCrypt
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.serializer.serializer import Serializer
from decentnet.modules.transfer.packager import Packager

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


async def assemble_disconnect_data(public_key_id: int, source: str,
                                   dest: str):
    """
    Assemble serialized block
    :param public_key_id:
    :param source:
    :param dest:
    :return:
    """
    __data = {"s": source, "d": dest}
    # disconnect_block = blockchain.template_next_block(cbor2.dumps(__data))
    # disconnect_block.mine()

    _data = await Packager.add_cmd(
        __data, public_key_id, NetworkCmd.DISCONNECT_EDGE.value
    )
    _data["cpub"] = AsymCrypt.verifying_key_to_string(_data["cpub"])
    # ttl = _data.get("ttl", 0)
    # logger.debug(
    #    f"Broadcasting disconnect {source} => {dest} to connected beams TTL {ttl}")
    # if not await blockchain.insert(disconnect_block):
    #    raise Exception("Failed to insert disconnect block")
    #
    # block_signature, block_bytes = await sign_block(public_key_id, disconnect_block)

    # serialized_block = Serializer.serialize_data(
    #    relay_pub_key_bytes,
    #    block_signature,
    #    block_bytes,
    #    "ALL",
    #    _data["cmd"],
    #    _data["csig"],
    #    _data["cpub"],
    #    ttl
    # )
    return _data


async def assemble_disconnect_block(public_key_id, relay_pub_key_bytes, blockchain, r2r_data) -> (
        Tuple)[bytes, Block]:
    """
    Assemble serialized block
    :param r2r_data:
    :param blockchain:
    :param relay_pub_key_bytes:
    :param public_key_id:
    :return:
    """
    disconnect_block = blockchain.template_next_block(cbor2.dumps(r2r_data))
    disconnect_block.mine()

    ttl = r2r_data.get("ttl", 0)
    if not await blockchain.insert(disconnect_block):
        raise Exception("Failed to insert disconnect block")
    #
    block_signature, block_bytes = await sign_block(public_key_id, disconnect_block)

    serialized_block = Serializer.serialize_data(
        relay_pub_key_bytes,
        block_signature,
        block_bytes,
        "ALL",
        r2r_data["cmd"],
        r2r_data["csig"],
        AsymCrypt.public_key_from_base64(r2r_data["cpub"], False),
        ttl
    )
    return serialized_block, disconnect_block


async def sign_block(public_key_id: int, block: Block) -> Tuple[bytes, bytes]:
    """Will sign block with current public key id of Relay"""
    block_bytes = await block.to_bytes()
    block_signature = await Packager.sign_block(
        public_key_id,
        block_bytes
    )
    return block_signature, block_bytes
