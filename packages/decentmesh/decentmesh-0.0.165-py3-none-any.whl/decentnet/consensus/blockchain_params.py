"""
Blockchain Parameters
"""
from dataclasses import dataclass

from decentnet.consensus.block_sizing import HASH_LEN
from decentnet.consensus.compress_params import (COMPRESSION_LEVEL_LZ4,
                                                 COMPRESSION_TYPE)
from decentnet.modules.pow.difficulty import Difficulty

SAVE_BLOCKS_TO_DB_DEFAULT = False
SKIP_SIGNATURE_VERIFICATION_DEPTH = 10  # Blocks
TIMESTAMP_TOLERANCE = 9  # nano seconds
BROADCAST_PROPAGATION_TTL = 5


@dataclass
class BlockchainParams:
    default_salt = b"Knz3z0&PavluT0m"
    default_salt_len = len(default_salt)
    default_genesis_msg = "CONNECTED"
    seed_difficulty = Difficulty(16, 8, 1, 16, HASH_LEN, COMPRESSION_LEVEL_LZ4, COMPRESSION_TYPE, 0)
    low_diff_argon = Difficulty(1, 8, 1, 1, HASH_LEN, COMPRESSION_LEVEL_LZ4, COMPRESSION_TYPE, 0)
    low_diff_sha256 = Difficulty(1, 8, 1, 1, HASH_LEN, COMPRESSION_LEVEL_LZ4, COMPRESSION_TYPE, 1)
    max_hosts = 65536
