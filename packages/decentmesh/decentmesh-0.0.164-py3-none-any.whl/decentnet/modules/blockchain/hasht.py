from dataclasses import dataclass

from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE


@dataclass
class HashT:
    value: bytes
    nonce: int

    def merge_to_int(self) -> int:
        return int.from_bytes(self.value, ENDIAN_TYPE) + self.nonce

    def merge_to_bytes(self) -> bytes:
        return (int.from_bytes(self.value, ENDIAN_TYPE) + self.nonce).to_bytes(2,
                                                                               byteorder=ENDIAN_TYPE)
