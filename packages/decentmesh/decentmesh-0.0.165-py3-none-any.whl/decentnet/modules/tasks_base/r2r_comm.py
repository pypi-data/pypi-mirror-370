import asyncio
import logging

import cbor2

from decentnet.consensus.cmd_enum import NetworkCmd
from decentnet.consensus.dev_constants import R2R_LOG_LEVEL
from decentnet.consensus.r2rcomm import BLOCK_COMMAND_PREFIX
from decentnet.modules.blockchain.block import Block
from decentnet.modules.comm.block_assembly import assemble_disconnect_block
from decentnet.modules.logger.log import setup_logger
from decentnet.modules.tasks_base.publisher import ClientBlockPublisher

logger = logging.getLogger(__name__)

setup_logger(R2R_LOG_LEVEL, logger)


class R2RComm:
    def __init__(self, relay):
        self.relay = relay
        logger.debug(f"Current pipes {relay.beam_pipe_comm.keys()}")
        process_uid = relay.received_beam_pub_key

        while relay.alive:
            self.relay_key = process_uid
            if process_uid in relay.beam_pipe_comm.keys():
                logger.debug(f"Receiving PIPE on {process_uid} for sync")
                data = relay.beam_pipe_comm[process_uid][0].recv()
                logger.debug("Received data from PIPE %s B" % (len(data)))
                if data[:3] == BLOCK_COMMAND_PREFIX:
                    # Assemble block from dict serialized
                    data_loaded = cbor2.loads(data[3:])
                    if data_loaded["cmd"] == NetworkCmd.DISCONNECT_EDGE.value:
                        serialized_block, block = asyncio.run(
                            self.process_disconnect_block(relay, data_loaded))
                    else:
                        raise RuntimeError(f"Unsupported cmd passed into R2RComm {data}")
                else:
                    block = Block.from_bytes(data)

                if not block:
                    continue

                if block.index == 0:
                    logger.debug("Overwriting blockchain with new genesis R2R")
                    relay.beam.comm_bc.clear()

                relay.beam.comm_bc.difficulty = block.diff
                relay.beam.comm_bc.insert_raw(block)

        logger.debug(f"Closing blockchain sync pipes for  {process_uid}")
        self.close_relay_pipe()

    def close_relay_pipe(self):
        self.relay.beam_pipe_comm[self.relay_key][0].close()
        self.relay.beam_pipe_comm[self.relay_key][1].close()
        self.relay.beam_pipe_comm.pop(self.relay_key)

    async def process_disconnect_block(self, relay, data_loaded):
        if relay.beam.target_key != data_loaded["d"]:
            logger.debug(f"Skipping disconnect block {data_loaded}")
            return None, None
        print(self.relay_key, relay.received_beam_pub_key, relay.beam.target_key, relay.beam.pub_key,
              relay.beam.conn_bc)
        serialized_block, block = await assemble_disconnect_block(relay.beam.pub_key_id,
                                                                  relay.relay_pub_key_bytes,
                                                                  relay.beam.conn_bc, data_loaded)
        logger.debug(f"Publishing disconnect block to {relay.beam.target_key}")
        print(f"RK: {data_loaded["cpub"]}"
              f" RK {relay.beam.target_key}"
              f" data: {data_loaded}")
        await ClientBlockPublisher.publish_message(relay.beam.target_key, serialized_block)
        return serialized_block, block
