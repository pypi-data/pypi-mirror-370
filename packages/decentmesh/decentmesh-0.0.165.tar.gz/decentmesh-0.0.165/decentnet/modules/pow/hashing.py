import hashlib

from argon2.low_level import hash_secret_raw

from decentnet.consensus.block_sizing import HASH_LEN
from decentnet.consensus.blockchain_params import BlockchainParams
from decentnet.consensus.hashing_params import ARGON2_TYPE
from decentnet.modules.pow.difficulty import Difficulty


def argon_hash_func(data: bytes, diff: Difficulty) -> bytes:
    """
    Hashes the given data using the Argon2id algorithm with parameters from the Difficulty object.

    Args:
        data: The input data to be hashed.
        diff: The Difficulty object containing Argon2 parameters (t_cost, m_cost, p_cost, hash_len_chars).

    Returns:
        The resulting hash as bytes.
    """
    return hash_secret_raw(
        data,  # Input data to be hashed
        BlockchainParams.default_salt,  # Use the predefined salt
        time_cost=diff.t_cost,  # Time cost (iterations)
        memory_cost=diff.m_cost,  # Memory cost (in KiB)
        parallelism=diff.p_cost,  # Number of parallel threads
        hash_len=diff.hash_len_chars,  # Length of the output hash (in bytes)
        type=ARGON2_TYPE  # Use Argon2d for a performance
    )


def sha256_hash_func(data: bytes):
    return hashlib.sha256(data).digest()[:HASH_LEN]
