from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.modules.pow.difficulty import Difficulty
from decentnet.modules.pow.hashing import argon_hash_func, sha256_hash_func


class MemoryHash:
    def __init__(self, diff: Difficulty, data: bytes):
        self.diff: Difficulty = diff
        self.value: bytes = argon_hash_func(data, diff)

    def __eq__(self, other):
        if isinstance(other, MemoryHash):
            return self.diff == other.diff and self.value == other.value
        return False

    def __hash__(self):
        return hash((self.diff, self.value))

    def __repr__(self):
        return f"MemoryHash(diff={self.diff}, value={self.value.hex()})"

    def recompute(self, data: bytes):
        self.value: bytes = argon_hash_func(data, self.diff)

    def value_as_hex(self):
        return self.value.hex()[2:].zfill(self.diff.hash_len_chars * 2)

    def value_as_int(self) -> int:
        return int.from_bytes(self.value, ENDIAN_TYPE)


class ShaHash:
    def __init__(self, diff: Difficulty, data: bytes):
        self.diff: Difficulty = diff
        self.value: bytes = sha256_hash_func(data)

    def __eq__(self, other):
        if isinstance(other, ShaHash):
            return self.diff == other.diff and self.value == other.value
        return False

    def __hash__(self):
        return hash((self.diff, self.value))

    def __repr__(self):
        return f"ShaHash(diff={self.diff}, value={self.value.hex()})"

    def recompute(self, data: bytes):
        self.value: bytes = sha256_hash_func(data)

    def value_as_hex(self):
        return self.value.hex()[2:].zfill(self.diff.hash_len_chars * 2)

    def value_as_int(self) -> int:
        return int.from_bytes(self.value, ENDIAN_TYPE)
