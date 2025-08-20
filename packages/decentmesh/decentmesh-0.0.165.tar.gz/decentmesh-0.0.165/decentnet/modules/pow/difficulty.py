import logging
from dataclasses import dataclass

from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.difficulty_byte_sizing import (
    COMPRESSION_LEVEL_BYTE_SIZE, COMPRESSION_LEVEL_CHUNK_SLICE,
    COMPRESSION_TYPE_BYTE_SIZE, COMPRESSION_TYPE_CHUNK_SLICE,
    EXPRESS_POW_BYTE_SIZE, EXPRESS_POW_CHUNK_SLICE, HASH_LEN_CHARS_BYTE_SIZE,
    HASH_LEN_CHARS_CHUNK_SLICE, M_COST_BYTE_SIZE, M_COST_CHUNK_SLICE,
    N_BITS_BYTE_SIZE, N_BITS_CHUNK_SLICE, P_COST_BYTE_SIZE, P_COST_CHUNK_SLICE,
    T_COST_BYTE_SIZE)
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


@dataclass
class Difficulty:
    t_cost: int
    m_cost: int
    p_cost: int
    n_bits: int
    hash_len_chars: int
    compression_level: int
    compression_type: int = 0
    express: int = 0

    # TODO: add block size and encryption type

    def to_bytes(self) -> bytes:
        return (
                self.t_cost.to_bytes(T_COST_BYTE_SIZE, byteorder=ENDIAN_TYPE, signed=False) +
                self.m_cost.to_bytes(M_COST_BYTE_SIZE, byteorder=ENDIAN_TYPE, signed=False) +
                self.p_cost.to_bytes(P_COST_BYTE_SIZE, byteorder=ENDIAN_TYPE, signed=False) +
                self.n_bits.to_bytes(N_BITS_BYTE_SIZE, byteorder=ENDIAN_TYPE, signed=False) +
                self.hash_len_chars.to_bytes(HASH_LEN_CHARS_BYTE_SIZE, byteorder=ENDIAN_TYPE, signed=False) +
                self.compression_level.to_bytes(COMPRESSION_LEVEL_BYTE_SIZE, byteorder=ENDIAN_TYPE,
                                                signed=False) +
                self.compression_type.to_bytes(COMPRESSION_TYPE_BYTE_SIZE, byteorder=ENDIAN_TYPE,
                                               signed=False) +
                self.express.to_bytes(EXPRESS_POW_BYTE_SIZE, byteorder=ENDIAN_TYPE, signed=False)
        )

    @classmethod
    def from_bytes(cls, difficulty_bytes: bytes | memoryview):
        t_cost = int.from_bytes(difficulty_bytes[0:T_COST_BYTE_SIZE], byteorder=ENDIAN_TYPE,
                                signed=False)
        m_cost = int.from_bytes(difficulty_bytes[T_COST_BYTE_SIZE:M_COST_CHUNK_SLICE],
                                byteorder=ENDIAN_TYPE,
                                signed=False)
        p_cost = int.from_bytes(difficulty_bytes[M_COST_CHUNK_SLICE:P_COST_CHUNK_SLICE],
                                byteorder=ENDIAN_TYPE,
                                signed=False)
        n_bits = int.from_bytes(difficulty_bytes[P_COST_CHUNK_SLICE:N_BITS_CHUNK_SLICE],
                                byteorder=ENDIAN_TYPE,
                                signed=False)
        hash_len_chars = int.from_bytes(difficulty_bytes[N_BITS_CHUNK_SLICE:HASH_LEN_CHARS_CHUNK_SLICE],
                                        byteorder=ENDIAN_TYPE,
                                        signed=False)
        compression_level = int.from_bytes(
            difficulty_bytes[HASH_LEN_CHARS_CHUNK_SLICE:COMPRESSION_LEVEL_CHUNK_SLICE], byteorder=ENDIAN_TYPE,
            signed=False)
        compression_type = int.from_bytes(
            difficulty_bytes[COMPRESSION_LEVEL_CHUNK_SLICE:COMPRESSION_TYPE_CHUNK_SLICE],
            byteorder=ENDIAN_TYPE,
            signed=False)
        express_pow = int.from_bytes(difficulty_bytes[COMPRESSION_TYPE_CHUNK_SLICE:EXPRESS_POW_CHUNK_SLICE],
                                     byteorder=ENDIAN_TYPE,
                                     signed=False)

        return cls(t_cost, m_cost, p_cost, n_bits, hash_len_chars, compression_level, compression_type,
                   express_pow)

    def __eq__(self, other):
        """
        Compares all.yaml attributes of the Difficulty instance except for the n_bits attribute.
        """
        if isinstance(other, Difficulty):
            return self.t_cost == other.t_cost and \
                self.m_cost == other.m_cost and \
                self.p_cost == other.p_cost and \
                self.hash_len_chars == other.hash_len_chars and \
                self.compression_level == other.compression_level and \
                self.compression_type == other.compression_type and \
                self.express == other.express
        return False

    def __repr__(self):
        return f"Difficulty(t_cost={self.t_cost}," \
               f" m_cost={self.m_cost}," \
               f" p_cost={self.p_cost}" \
               f", n_bits={self.n_bits}," \
               f" hash_len_chars={self.hash_len_chars})" \
               f", compression_level={self.compression_level})" \
               f", compression_type={self.compression_type})" \
               f", express={self.express})"

    def __hash__(self):
        return hash(
            (self.t_cost, self.m_cost, self.p_cost, self.n_bits, self.hash_len_chars, self.compression_level,
             self.compression_type,
             self.express))

    def __iter__(self):
        yield from [self.t_cost, self.m_cost, self.p_cost, self.n_bits,
                    self.hash_len_chars, self.compression_level, self.compression_type, self.express]

    def __str__(self):
        return f"{self.t_cost}:{self.m_cost}:{self.p_cost}:{self.n_bits}:{self.hash_len_chars}:{self.compression_level}:{self.compression_type}:{self.express}"

    def __post_init__(self):
        if (req_m_cost := 8 * self.p_cost) > self.m_cost:
            logger.debug(
                f"Memory too low increasing from {self.m_cost} to {req_m_cost}")
            self.m_cost = req_m_cost
