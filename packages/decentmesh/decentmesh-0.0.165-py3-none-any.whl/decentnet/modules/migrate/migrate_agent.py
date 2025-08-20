import logging
import os
from pathlib import Path

from alembic import command
from alembic.config import Config

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.local_config import (DATABASE_URL_ASYNC,
                                              DATABASE_URL_SYNC)
from decentnet.modules.db.constants import USING_ASYNC_DB
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class MigrateAgent:
    @staticmethod
    def do_migrate():
        logger.info("Migrating DB")
        alembic_cfg = Config(os.getenv("ALEMBIC_CONFIG",
                                       str(Path(
                                           __file__).resolve()
                                           .parent.parent.parent.parent /
                                           "alembic.ini")))
        alembic_cfg.set_main_option("sqlalchemy.url",
                                    DATABASE_URL_ASYNC if USING_ASYNC_DB else DATABASE_URL_SYNC)
        # command.revision(alembic_cfg, "DB Change")
        try:
            command.upgrade(alembic_cfg, "head")
        except:
            pass
