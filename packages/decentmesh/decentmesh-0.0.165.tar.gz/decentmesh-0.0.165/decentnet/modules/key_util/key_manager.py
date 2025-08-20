import asyncio
import logging

from nacl.signing import SigningKey, VerifyKey
from sqlalchemy import and_, delete, select

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.cryptography.asymmetric import AsymCrypt
from decentnet.modules.db.base import session_scope
from decentnet.modules.db.constants import USING_ASYNC_DB
from decentnet.modules.db.models import OwnedKeys
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)

from decentnet.modules.convert.byte_to_base64_utils import bytes_to_base64


class KeyManager:
    @classmethod
    def generate_keys(cls, description: str, private_key_file: str = None, public_key_file: str = None,
                      sign: bool = False, alias: str = None):
        from decentnet.utils.key_tools import generate_impl
        try:
            return asyncio.run(generate_impl(description, private_key_file, public_key_file, sign, alias))
        except Exception as e:
            logger.debug(f"Failed to generate keys because of {e}")
            return False

    @classmethod
    def generate_singing_key_pair(cls):
        sign_keys = AsymCrypt.generate_key_pair_signing()
        private_key = sign_keys[0].encode()
        public_key = sign_keys[1]
        return private_key, public_key

    @classmethod
    def generate_encryption_key_pair(cls):
        sign_keys = AsymCrypt.generate_key_pair_encryption()
        private_key = sign_keys[0]
        public_key = sign_keys[1]
        return private_key, public_key

    @classmethod
    def key_to_base64(cls, key: bytes):
        return bytes_to_base64(key)

    @classmethod
    def import_ssh_key_pair(cls, private_key_path, public_key_path):
        # TODO Implement
        raise NotImplementedError()

    @classmethod
    def export_ssh_key_pair(cls, private_key_obj, public_key_obj):
        private_key_str = private_key_obj.get_base64()
        public_key_str = f"{public_key_obj.get_name()} {public_key_obj.get_base64().decode('utf-8')}"
        return private_key_str, public_key_str

    @classmethod
    async def clear_db(cls):
        if USING_ASYNC_DB:
            async def clear_async():
                async with session_scope() as session:
                    # Delete all records from OwnedKeys table
                    await session.execute(delete(OwnedKeys))

            return await clear_async()
        else:
            with session_scope() as session:
                session.execute(delete(OwnedKeys))

    @classmethod
    async def save_to_db(cls, private_key, public_key, description, can_encrypt, alias):
        if USING_ASYNC_DB:
            async def save_async():
                async with session_scope() as session:
                    ssh_key_pair = OwnedKeys(
                        private_key=private_key,
                        public_key=public_key,
                        description=description,
                        can_encrypt=can_encrypt,
                        alias=alias
                    )
                    session.add(ssh_key_pair)
                    await session.flush()
                    return ssh_key_pair.id

            return await save_async()
        else:
            with session_scope() as session:
                ssh_key_pair = OwnedKeys(
                    private_key=private_key,
                    public_key=public_key,
                    description=description,
                    can_encrypt=can_encrypt,
                    alias=alias
                )
                session.add(ssh_key_pair)
                session.flush()
                return ssh_key_pair.id

    @classmethod
    async def retrieve_ssh_key_pair_from_db(cls, key_id: int, can_encrypt: bool = False) -> \
            tuple[
                SigningKey,
                VerifyKey] | \
            tuple[
                bytes, bytes]:
        """Retrieve SSH key pair from the database.

        Args:
            key_id (int): The unique identifier of the SSH key pair to retrieve.

        Returns:
            Tuple[str, str] or Tuple[None, None]: A tuple containing the private key
            and public key retrieved from the database. If the specified key_id is not found,
            it returns (None, None).
            :param key_id: Key id to retrieve
            :param can_encrypt: property of a key
        """
        if USING_ASYNC_DB:
            async with session_scope() as session:
                # Use an asynchronous query to find the key pair
                key_pair = await session.get(OwnedKeys, key_id)

                # optionally verify boolean if you truly need it
                if key_pair and can_encrypt is not None and bool(key_pair.can_encrypt) != bool(can_encrypt):
                    key_pair = None
                    logger.fatal(f"This key does not match can_encrypt={can_encrypt}.")

                if key_pair:
                    return AsymCrypt.key_pair_from_private_key_base64(
                        key_pair.private_key, key_pair.can_encrypt
                    )
                else:
                    raise Exception(f"No Key with id {key_id} found")
        else:
            with session_scope() as session:
                # Use a synchronous query to find the key pair
                result = session.execute(
                    select(OwnedKeys).where(
                        and_(OwnedKeys.id == key_id, OwnedKeys.can_encrypt == can_encrypt)
                    )
                )
                key_pair = result.scalar_one_or_none()

                if key_pair:
                    return AsymCrypt.key_pair_from_private_key_base64(
                        key_pair.private_key, key_pair.can_encrypt
                    )
                else:
                    raise Exception(f"No Key with id {key_id} found")

    @classmethod
    async def get_private_key(cls, public_key: str):
        if USING_ASYNC_DB:
            async with session_scope() as session:
                result = await session.execute(
                    select(OwnedKeys).where(OwnedKeys.public_key == public_key)
                )
                key_pair = result.scalar_one_or_none()

                if key_pair:
                    return AsymCrypt.key_pair_from_private_key_base64(
                        key_pair.private_key, key_pair.can_encrypt
                    )[0]
                else:
                    raise Exception(f"No Private Key found for public key {public_key}")
        else:
            with session_scope() as session:
                result = session.execute(
                    select(OwnedKeys).where(OwnedKeys.public_key == public_key)
                )
                key_pair = result.scalar_one_or_none()

                if key_pair:
                    return AsymCrypt.key_pair_from_private_key_base64(
                        key_pair.private_key, key_pair.can_encrypt
                    )[0]
                else:
                    raise Exception(f"No Private Key found for public key {public_key}")

    @classmethod
    async def get_all_keys(cls):
        if USING_ASYNC_DB:
            async with session_scope() as session:
                result = await session.execute(select(OwnedKeys))
                keys = result.scalars().all()
                return keys
        else:
            with session_scope() as session:
                result = session.execute(select(OwnedKeys))
                keys = result.scalars().all()
                return keys
