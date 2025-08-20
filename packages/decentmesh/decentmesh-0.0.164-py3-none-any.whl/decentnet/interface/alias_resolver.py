import asyncio
from typing import Optional, Tuple

from sqlalchemy import select

from decentnet.modules.db.base import session_scope
from decentnet.modules.db.constants import USING_ASYNC_DB
from decentnet.modules.db.models import OwnedKeys


class AliasResolver:
    """
    AliasResolver is responsible for resolving the public key and key ID based on a given alias.
    """

    @classmethod
    def get_key_by_alias(cls, alias: str) -> Optional[Tuple[str, int]]:
        return asyncio.run(cls.__get_key_by_alias(alias))

    @classmethod
    async def __get_key_by_alias(cls, alias: str) -> Optional[Tuple[str, int]]:
        """
        Retrieves the public key and key ID based on the given alias.

        Args:
            alias (str): The alias to search for

        Returns:
            Optional[Tuple[str, int]]: A tuple containing the public key and key ID if found, otherwise None.
        """
        if USING_ASYNC_DB:
            async with session_scope() as session:
                # Perform the asynchronous query
                result = await session.execute(
                    select(OwnedKeys).where(OwnedKeys.alias == alias)
                )
                key = result.scalar_one_or_none()  # Fetch the first result or None

                if key:
                    return key.public_key, key.id

                return None
        else:
            with session_scope() as session:
                # Perform the synchronous query
                result = session.execute(
                    select(OwnedKeys).where(OwnedKeys.alias == alias)
                )
                key = result.scalar_one_or_none()  # Fetch the first result or None

                if key:
                    return key.public_key, key.id

                return None
