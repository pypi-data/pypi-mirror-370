"""Block Byte allocation for serialization and deserialization"""
from decentnet.consensus.difficulty_byte_sizing import (
    COMPRESSION_LEVEL_BYTE_SIZE, COMPRESSION_TYPE_BYTE_SIZE,
    EXPRESS_POW_BYTE_SIZE, HASH_LEN_CHARS_BYTE_SIZE, M_COST_BYTE_SIZE,
    N_BITS_BYTE_SIZE, P_COST_BYTE_SIZE, T_COST_BYTE_SIZE)

# This blocks maximum size is intentionally smaller
# to prevent DDOS attacks and ensure decentralized sending
MAXIMUM_BLOCK_SIZE = 4194304  # Bytes
BLOCK_PREFIX_LENGTH_BYTES = 3  # Bytes
INDEX_SIZE = 5  # Bytes, It would take 100 years at 10ms a block to overflow
NONCE_SIZE = 4  # Bytes, Standard nonce size
TIMESTAMP_SIZE = 8  # Bytes, Sufficient for 2.28 million years.

MERGED_DIFFICULTY_BYTE_LEN = (T_COST_BYTE_SIZE +
                              M_COST_BYTE_SIZE +
                              P_COST_BYTE_SIZE +
                              N_BITS_BYTE_SIZE +
                              HASH_LEN_CHARS_BYTE_SIZE +
                              COMPRESSION_LEVEL_BYTE_SIZE +
                              COMPRESSION_TYPE_BYTE_SIZE +
                              EXPRESS_POW_BYTE_SIZE)
# Bytes
HASH_LEN = 32  # Bytes
HASH_LEN_BLOCK = 48  # Bytes

RESERVED_EMPTY_BYTE_LEN = 77  # Bytes

MAXIMUM_DATA_SIZE = (MAXIMUM_BLOCK_SIZE - BLOCK_PREFIX_LENGTH_BYTES - INDEX_SIZE -
                     NONCE_SIZE - TIMESTAMP_SIZE -
                     MERGED_DIFFICULTY_BYTE_LEN - HASH_LEN -
                     HASH_LEN_BLOCK - RESERVED_EMPTY_BYTE_LEN)
