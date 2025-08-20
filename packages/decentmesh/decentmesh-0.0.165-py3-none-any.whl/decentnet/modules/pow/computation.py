from typing import Any

from argon2.low_level import hash_secret_raw

from decentnet.consensus.blockchain_params import BlockchainParams
from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.consensus.hashing_params import ARGON2_TYPE
from decentnet.modules.convert.byte_operations import int_to_bytes
from decentnet.modules.pow.hashing import sha256_hash_func


def compute_argon2_pow(n_bits: int, hash_t: Any, nonce: int) -> int:
    """
    Computes the Argon2 Proof of Work (PoW) by incrementing the nonce until the hash meets the required number of bits.

    Args:
        n_bits: The number of leading zero bits required.
        hash_t: The object containing the hash parameters (t_cost, m_cost, p_cost, hash_len_chars).
        nonce: The starting nonce value.

    Returns:
        The correct nonce that produces a hash with the required number of leading zero bits.
    """
    _bits = hash_t.diff.hash_len_chars * 8 - n_bits  # Adjust target bit length

    # Loop until a valid nonce is found
    while int.from_bytes(
            hash_secret_raw(
                int_to_bytes(hash_t.value_as_int() + nonce),  # Increment hash value by nonce
                BlockchainParams.default_salt,  # Use predefined salt
                time_cost=hash_t.diff.t_cost,  # Time cost for Argon2
                memory_cost=hash_t.diff.m_cost,  # Memory cost for Argon2
                parallelism=hash_t.diff.p_cost,  # Parallelism for Argon2
                hash_len=hash_t.diff.hash_len_chars,  # Output hash length (in bytes)
                type=ARGON2_TYPE  # Use Argon2id for hybrid defense
            ),
            ENDIAN_TYPE  # Convert from bytes to integer using the specified endianness
    ).bit_length() > _bits:
        nonce += 1

    # Return the nonce that meets the required condition
    return nonce


def compute_sha256_pow(n_bits, hash_t, nonce):
    _bits = hash_t.diff.hash_len_chars * 8 - n_bits

    # Loop until the condition is satisfied
    while int.from_bytes(
            sha256_hash_func(int_to_bytes(hash_t.value_as_int() + nonce)),
            ENDIAN_TYPE).bit_length() > _bits:
        nonce += 1

    # Return the correct nonce without modifying the original hash_t
    return nonce
