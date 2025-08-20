import logging
from builtins import memoryview
from typing import Tuple

import lz4.frame

from decentnet.consensus.compress_params import COMPRESSION_LEVEL_LZ4
from decentnet.consensus.dev_constants import (COMPRESSION_LOG_LEVEL,
                                               RUN_IN_DEBUG, DEBUG_LZ4)
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)
logger.setLevel(COMPRESSION_LOG_LEVEL)

setup_logger(RUN_IN_DEBUG, logger)


class CompressionHBW:
    """High bandwidth compression wrapper."""

    @staticmethod
    def compress_lz4(data: bytes,
                     compression_level: int = COMPRESSION_LEVEL_LZ4) -> Tuple[bytes, int]:
        """
        Compresses data using LZ4 compression algorithm with the specified compression level.

        Args:
            data (bytes): The data to compress.
            compression_level (int): The compression level (0-16), higher values result in better compression but slower speed. Defaults to 8.

        Returns:
            bytes: The compressed data.
            int: Size of data
        """

        data_size_before = len(data)
        if DEBUG_LZ4:
            logger.debug(f"Compressing data with LZ4 initial size {data_size_before} B")
        compressed = lz4.frame.compress(data, compression_level=compression_level)
        data_size_after = len(compressed)

        if DEBUG_LZ4:
            logger.debug(f"Compressed data to {data_size_after} B")
        if data_size_before < data_size_after:
            if DEBUG_LZ4:
                logger.debug("Disabled compression due to data incompatibility")
            return data, data_size_before
        return compressed, data_size_after

    @staticmethod
    def decompress_lz4(compressed_data: bytes | memoryview | bytearray) -> bytes:
        """
        Decompresses data using LZ4 decompression algorithm.

        Args:
            compressed_data (bytes): The compressed data to decompress.

        Returns:
            bytes: The decompressed data.
        """
        if DEBUG_LZ4:
            logger.debug("Decompressing data with LZ4")
        try:
            return lz4.frame.decompress(compressed_data)
        except RuntimeError:
            return compressed_data
