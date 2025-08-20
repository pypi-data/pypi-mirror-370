import io
import logging
import struct
import time
from typing import Tuple, Union

from Crypto.Util.Padding import pad, unpad

from decentnet.consensus.block_sizing import (HASH_LEN, HASH_LEN_BLOCK,
                                              INDEX_SIZE,
                                              MERGED_DIFFICULTY_BYTE_LEN,
                                              NONCE_SIZE, TIMESTAMP_SIZE)
from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE
from decentnet.consensus.compress_params import COMPRESSION_TYPE
from decentnet.consensus.dev_constants import (BLOCK_ERROR_DATA_LOG_LEN,
                                               METRICS, RUN_IN_DEBUG)

if COMPRESSION_TYPE == 0:
    from decentnet.modules.compression.hbw_wrapper import CompressionHBW

from decentnet.modules.compression.zl_wrapper import CompressionSBW
from decentnet.modules.hash_type.hash_type import MemoryHash, ShaHash
from decentnet.modules.logger.log import setup_logger

if METRICS:
    from decentnet.modules.monitoring.metric_server import send_metric

from decentnet.modules.pow.difficulty import Difficulty
from decentnet.modules.pow.pow import PoW
from decentnet.modules.timer.timer import Timer

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class Block:
    _metrics_logged = False
    index: int
    previous_hash: bytes = None
    diff: Difficulty
    data: bytearray
    timestamp: float
    nonce: int | None
    _hash: MemoryHash | ShaHash | None
    ttc: float
    signature: str | None = None
    do_metric: bool = False

    def __init__(self, index: int, prev_hash: bytes,
                 difficulty: Difficulty,
                 data: Union[bytearray, bytes], do_metric: bool = METRICS):
        self.index = index
        self.previous_hash = prev_hash
        self.data = data
        self.diff = difficulty
        self.timestamp = time.time_ns()
        self.nonce = 0
        self.signature = None
        self.do_metric = do_metric

        if not Block._metrics_logged:
            if not self.do_metric:
                logger.debug("Metrics in Block will not be collected.. FAIL")
                Block._metrics_logged = True

    def __str__(self):
        dd = str(bytes(self.data))
        display_data = dd[:BLOCK_ERROR_DATA_LOG_LEN] + "..." if len(
            dd) > BLOCK_ERROR_DATA_LOG_LEN else dd
        result = f"Block #{self.index}\n" \
                 f"Previous Hash: {self.previous_hash.hex()[2:].zfill(HASH_LEN) if self.index != 0 else 'GENESIS BLOCK'}\n" \
                 f"Difficulty: {self.diff}\n" \
                 f"Data: {display_data}\n" \
                 f"Timestamp: {self.timestamp}\n" \
                 f"Nonce: {self.nonce}\n"

        result += f"Hash: {self.hash.value.hex()[2:].zfill(HASH_LEN)}\n"

        return result

    @property
    def hash(self):
        if "_hash" not in self.__dict__:
            self.compute_hash()
        return self._hash

    @staticmethod
    def concat_bytes(*args: Union[bytes, bytearray]) -> Tuple[bytes, int]:
        """
        Concatenates a dynamic number of byte-like objects (bytes or bytearray) into a single bytes object.
        All provided arguments are written to an in-memory buffer (BytesIO), and the buffer is closed after use.

        Args:
            *args: A variable number of byte-like objects to be concatenated. Each argument must be either `bytes` or `bytearray`.

        Returns:
            bytes: A single concatenated bytes object containing the data from all provided arguments.
            int: total count of concatenated bytes.

        Example:
            result = concat_bytes(index_bytes, diff_bytes, previous_hash_bytes, nonce_bytes, timestamp_bytes, compressed_data)
        """
        # Create an in-memory buffer
        total_written = 0
        buffer = io.BytesIO()

        # Write each byte-like argument to the buffer
        for arg in args:
            total_written += buffer.write(arg)

        # Get the concatenated bytes from the buffer
        result = buffer.getvalue()

        # Ensure the buffer is closed to release resources
        buffer.close()

        return result, total_written

    def compute_hash(self) -> MemoryHash | ShaHash:
        index_bytes = self.index.to_bytes(INDEX_SIZE, byteorder=ENDIAN_TYPE, signed=False)
        diff_bytes = self.diff.to_bytes()
        previous_hash_bytes = self.previous_hash
        timestamp_bytes = struct.pack('d', self.timestamp)

        packed_block, _ = self.concat_bytes(index_bytes,
                                            diff_bytes,
                                            previous_hash_bytes,
                                            timestamp_bytes,
                                            self.data)

        if not self.diff.express:
            self._hash = MemoryHash(self.diff, packed_block)
        else:
            self._hash = ShaHash(self.diff, packed_block)

        return self._hash

    async def to_bytes(self) -> bytes:
        index_bytes = self.index.to_bytes(INDEX_SIZE, byteorder=ENDIAN_TYPE, signed=False)
        diff_bytes = self.diff.to_bytes()

        previous_hash_bytes = pad(bytes(self.previous_hash), HASH_LEN_BLOCK, style='pkcs7')

        nonce_bytes = self.nonce.to_bytes(NONCE_SIZE, byteorder=ENDIAN_TYPE,
                                          signed=False)
        timestamp_bytes = struct.pack('q', self.timestamp)

        if self.diff.compression_level > 0:
            if self.diff.compression_type == 0:
                data, data_size = CompressionHBW.compress_lz4(self.data, self.diff.compression_level)
            elif self.diff.compression_type == 1:
                zl_level = CompressionSBW.get_compression_level_lz4_to_zlib(self.diff.compression_level)
                data = CompressionSBW.compress_zlib(self.data, zl_level)
                if self.do_metric:
                    data_size = len(data)
        else:
            data = self.data
            data_size = len(self.data)

        packed_block, packed_block_len = self.concat_bytes(index_bytes,
                                                           diff_bytes,
                                                           previous_hash_bytes,
                                                           nonce_bytes,
                                                           timestamp_bytes,
                                                           data)

        if self.do_metric:
            original_size = len(self.data)
            await send_metric("data_header_ratio", data_size / original_size)
            logger.debug(
                f"Data ratio {data_size / original_size} {data_size} {original_size}")

        logger.debug(f"Packed Block into {packed_block_len} B")
        return packed_block

    @classmethod
    def from_bytes(cls, compressed_block_bytes: bytes):
        block = cls.__new__(cls)

        block_bytes = memoryview(compressed_block_bytes)

        cursor = 0

        # Unpack index
        block.index = int.from_bytes(block_bytes[cursor:cursor + INDEX_SIZE], byteorder=ENDIAN_TYPE,
                                     signed=False)
        cursor += INDEX_SIZE

        # Unpack difficulty
        block.diff = Difficulty.from_bytes(block_bytes[cursor:cursor + MERGED_DIFFICULTY_BYTE_LEN])
        cursor += MERGED_DIFFICULTY_BYTE_LEN

        # Unpack previous hash
        block.previous_hash = unpad(bytes(block_bytes[cursor:cursor + HASH_LEN_BLOCK]), HASH_LEN_BLOCK,
                                    style='pkcs7')
        cursor += HASH_LEN_BLOCK

        # Unpack nonce
        block.nonce = int.from_bytes(block_bytes[cursor:cursor + NONCE_SIZE],
                                     byteorder=ENDIAN_TYPE,
                                     signed=False)
        cursor += NONCE_SIZE

        # Unpack timestamp
        block.timestamp = struct.unpack("q", block_bytes[cursor:cursor + TIMESTAMP_SIZE])[0]
        cursor += TIMESTAMP_SIZE

        # Decompress the remaining data
        if block.diff.compression_type == 0:
            block.data = block_bytes[
                         cursor:] if block.diff.compression_level == 0 else CompressionHBW.decompress_lz4(
                block_bytes[cursor:])
        elif block.diff.compression_type == 1:
            block.data = block_bytes[
                         cursor:] if block.diff.compression_level == 0 else CompressionSBW.decompress_zlib(
                block_bytes[cursor:])

        return block

    def mine(self, measure=False):
        logger.debug(f"Mining block #{self.index}")
        if measure:
            t = Timer()

        a = self.compute_hash()

        finished_hash, finished_nonce = PoW.compute(a, self.diff.n_bits, express=self.diff.express)
        self.nonce = finished_nonce

        if measure:
            self.ttc = t.stop()
            return finished_nonce, self.ttc
        else:
            return finished_nonce
