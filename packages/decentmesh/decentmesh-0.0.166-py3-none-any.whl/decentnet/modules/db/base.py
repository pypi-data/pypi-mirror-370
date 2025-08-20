import asyncio
import logging
import os
from contextlib import asynccontextmanager, contextmanager
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine as sync_create_engine, text
from sqlalchemy.orm import sessionmaker

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.consensus.local_config import (DATABASE_URL_ASYNC,
                                              DATABASE_URL_SYNC, DB_FILENAME)
from decentnet.modules.db import constants
from decentnet.modules.db.models import Base
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)

try:
    import greenlet
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    constants.USING_ASYNC_DB = True
except ImportError:
    constants.USING_ASYNC_DB = False
    logger.warning("Greenlet not installed using synchronous sqlite instead")


@lru_cache()
def get_root_dir() -> Path:
    return Path(os.path.abspath(__file__)).parent.parent.parent.parent


async def init_db(eng):
    if constants.USING_ASYNC_DB:
        # Async initialization
        async with eng.connect() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA busy_timeout = 60"))
    else:
        # Sync initialization as fallback
        with eng.connect() as conn:
            Base.metadata.create_all(conn)
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.execute(text("PRAGMA busy_timeout = 60"))

        # Switch between async or sync engine depending on Greenlet availability


db_file = get_root_dir() / DB_FILENAME
if constants.USING_ASYNC_DB:
    engine = create_async_engine(DATABASE_URL_ASYNC, echo=False)
else:
    engine = sync_create_engine(DATABASE_URL_SYNC, echo=False)

asyncio.run(init_db(engine))

if constants.USING_ASYNC_DB:
    # Modify session_scope to handle both async and sync sessions
    @asynccontextmanager
    async def session_scope():
        """Provide a transactional scope around a series of operations asynchronously."""
        async_session = async_sessionmaker(
            bind=engine,
            expire_on_commit=False
        )()
        try:
            yield async_session
            await async_session.commit()
        except Exception as e:
            await async_session.rollback()
            raise e
        finally:
            await async_session.close()

else:
    @contextmanager
    def session_scope():
        """Provide a transactional scope around a series of operations synchronously."""
        sync_session = sessionmaker(
            bind=engine,
            expire_on_commit=False
        )()
        try:
            yield sync_session
            sync_session.commit()
        except Exception as e:
            sync_session.rollback()
            raise e
        finally:
            sync_session.close()
