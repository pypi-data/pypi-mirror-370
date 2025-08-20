"""
Compression parameters
"""
import os

COMPRESSION_LEVEL_LZ4 = int(os.getenv('COMPRESSION_LEVEL_LZ4', 9))
COMPRESSION_TYPE = int(os.getenv("COMPRESSION_TYPE", 0))  # 0 - LZ4, 1 - ZLIB
