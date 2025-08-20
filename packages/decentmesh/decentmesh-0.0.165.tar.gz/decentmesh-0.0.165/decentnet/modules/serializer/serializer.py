import logging
from typing import Optional

import cbor2
from nacl.signing import VerifyKey

from decentnet.consensus.dev_constants import RUN_IN_DEBUG, DEBUG_DATA_SERIALIZATION
from decentnet.modules.cryptography.asymmetric import AsymCrypt
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class Serializer:
    @staticmethod
    def serialize_data(
            public_key: VerifyKey | str,
            signature: bytes,
            encrypted_data: bytes,
            target_pub_key: Optional[str] = None,
            cmd: Optional[int] = None,
            command_signature: Optional[bytes] = None,
            command_public_key: Optional[VerifyKey] = None,
            ttl: Optional[int] = None,
    ) -> bytes:
        """Serializes public key, signature, and encrypted data and returns them as separate bytes.

        :returns: utf-8 encoded JSON
        """
        # Convert public_key to string if it's not already
        public_key_str = (
            public_key if isinstance(public_key, str)
            else AsymCrypt.verifying_key_to_string(public_key)
        )

        out = {
            "pub": public_key_str,
            "sig": signature,
            "data": encrypted_data,
            "target": target_pub_key
        }

        # Include command-related data only if cmd and command_signature are provided
        if cmd and command_signature:
            out.update({
                "cmd": cmd,
                "csig": command_signature,
                "cpub": AsymCrypt.verifying_key_to_string(command_public_key),
                "ttl": ttl
            })
        if RUN_IN_DEBUG and DEBUG_DATA_SERIALIZATION:
            logger.debug("Serialized data into: %s", out)
        return cbor2.dumps(out)

    @staticmethod
    def deserialize_data(serialized_data: bytes) -> dict:
        """Deserializes the provided data and returns the public key, signature, and encrypted data."""
        deserialized_data = cbor2.loads(serialized_data)

        if not isinstance(deserialized_data, dict) or deserialized_data.get("sig", None) is None:
            raise Exception(f"Corrupted data {deserialized_data}")

        return deserialized_data
