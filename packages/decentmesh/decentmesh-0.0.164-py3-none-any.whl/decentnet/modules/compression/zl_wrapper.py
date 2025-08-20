import logging
import zlib
from builtins import memoryview

from decentnet.consensus.dev_constants import (COMPRESSION_LOG_LEVEL,
                                               RUN_IN_DEBUG)
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)
logger.setLevel(COMPRESSION_LOG_LEVEL)

setup_logger(RUN_IN_DEBUG, logger)


class CompressionSBW:
    """Small bandwidth compression wrapper."""

    @staticmethod
    def get_compression_level_lz4_to_zlib(level: int) -> int:
        return int((level * 9 / 20) + 0.5)  # Adding 0.5 for rounding to nearest integer

    @staticmethod
    def compress_zlib(data: bytes, level: int = 6) -> bytes:
        """
        Compresses data using zlib compression algorithm with the specified compression level.

        Args:
            data (bytes): The data to compress.
            level (int): The compression level. Higher values result in better compression but slower speed. Defaults to 6.

        Returns:
            bytes: The compressed data.
        """
        return zlib.compress(data, level=level)

    @staticmethod
    def decompress_zlib(compressed_data: bytes | memoryview | bytearray) -> bytes:
        """
        Decompresses data using zlib decompression algorithm.

        Args:
            compressed_data (bytes): The compressed data to decompress.

        Returns:
            bytes: The decompressed data.
        """
        return zlib.decompress(compressed_data)
