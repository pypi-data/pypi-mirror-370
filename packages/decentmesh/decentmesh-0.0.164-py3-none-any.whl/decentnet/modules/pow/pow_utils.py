from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.modules.convert.byte_operations import int_to_bytes
from decentnet.modules.hash_type.hash_type import MemoryHash, ShaHash
from decentnet.modules.pow.difficulty import Difficulty
from decentnet.modules.pow.hashing import argon_hash_func, sha256_hash_func


class PowUtils:
    @staticmethod
    def get_bit_length(i_hash: MemoryHash | ShaHash, nonce: int, diff: Difficulty) -> int:
        if not diff.express:
            return PowUtils.value_as_int(
                argon_hash_func(int_to_bytes(i_hash.value_as_int() + nonce), diff)).bit_length()
        else:
            return PowUtils.value_as_int(
                sha256_hash_func(int_to_bytes(i_hash.value_as_int() + nonce))).bit_length()

    @staticmethod
    def value_as_int(value) -> int:
        return int.from_bytes(value, ENDIAN_TYPE)
