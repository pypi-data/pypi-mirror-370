from typing import List

from sqlalchemy import select

from decentnet.modules.db.base import session_scope
from decentnet.modules.db.constants import USING_ASYNC_DB
from decentnet.modules.db.models import AliveBeam


async def get_alive_beams() -> List[AliveBeam]:
    if USING_ASYNC_DB:
        async with session_scope() as session:
            # Perform an asynchronous query to retrieve all living beams
            result = await session.execute(select(AliveBeam).where(AliveBeam.ready))
            all_alive_beams = result.scalars().all()
        return all_alive_beams
    else:
        with session_scope() as session:
            # Perform a synchronous query to retrieve all living beams
            result = session.execute(select(AliveBeam).where(AliveBeam.ready))
            all_alive_beams = result.scalars().all()
        return all_alive_beams
