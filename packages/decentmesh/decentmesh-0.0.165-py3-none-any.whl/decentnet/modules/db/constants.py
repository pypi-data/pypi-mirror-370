import os

from decentnet.consensus.env_convert_funcs import e2b

USING_ASYNC_DB = e2b(os.getenv("USING_ASYNC_DB", True))
