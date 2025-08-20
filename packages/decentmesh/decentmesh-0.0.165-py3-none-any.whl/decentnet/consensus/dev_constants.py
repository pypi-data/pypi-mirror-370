"""
Debug Constants
"""
import logging
import os

from decentnet.consensus.env_convert_funcs import e2b

DEBUG_DATA_SERIALIZATION = e2b(os.getenv("DEBUG_DATA_SERIALIZATION", False))
DEBUG_SEED_CONNECTIONS = e2b(os.getenv("DEBUG_SEED_CONNECTIONS", False))
DEBUG_RELAY_USING = e2b(os.getenv("DEBUG_RELAY_USING", False))
RUN_IN_DEBUG = e2b(os.getenv("DEBUG", False))
LOG_LEVEL = os.getenv("DEBUG_LEVEL", logging.DEBUG)
ENCRYPTION_DEBUG = e2b(os.getenv("ENCRYPTION_DEBUG", False))
METRICS = e2b(os.getenv("METRICS", False))

DEBUG_TIMING = e2b(os.getenv("DEBUG_TIMING", False))
DEBUG_LZ4 = e2b(os.getenv("DEBUG_LZ4", False))
BLOCK_SHARE_LOG_LEVEL = os.getenv("BLOCK_SHARE_LOG_LEVEL", logging.ERROR)
SEEDS_AGENT_LOG_LEVEL = os.getenv("SEEDS_AGENT_LOG_LEVEL", logging.INFO)
COMPRESSION_LOG_LEVEL = os.getenv("COMPRESSION_LOG_LEVEL", logging.WARNING)
R2R_LOG_LEVEL = os.getenv("R2R_LOG_LEVEL", logging.INFO)
BLOCK_ERROR_DATA_LOG_LEN = 50
