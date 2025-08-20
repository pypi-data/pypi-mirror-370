import logging
from typing import Optional

from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.cryptography.asymmetric import AsymCrypt
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class AsymmetricManager:
    def __init__(
            self,
            private_key: Optional[bytes | SigningKey] = None,
            public_key: Optional[bytes | VerifyKey] = None,
            can_encrypt: bool = False,
    ):
        self.private_key = private_key
        self.public_key = public_key
        self.can_encrypt = can_encrypt

    def encrypt_message(self, data: bytes):
        """Decrypts data using Elliptic curve."""
        if not self.can_encrypt:
            raise AttributeError("Cannot encrypt with a singing key")
        if not isinstance(self.public_key, bytes):
            raise ValueError("Public key not available for encryption")

        encrypted_data = AsymCrypt.encrypt_message(self.public_key, data)
        return encrypted_data

    def decrypt_message(self, encrypted_data: bytes):
        """Decrypts data using Elliptic curve."""
        if not self.can_encrypt:
            raise AttributeError("Cannot decrypt with a signing key")
        if not isinstance(self.private_key, bytes):
            raise ValueError("Private key not available for decryption")

        decrypted_data = AsymCrypt.decrypt_message(self.private_key, encrypted_data)
        return decrypted_data

    def sign_message(self, data: bytes):
        """Signs data using ECDSA if not encryptable."""
        if self.can_encrypt:
            raise AttributeError("Cannot sign with a encryption key")
        elif not isinstance(self.private_key, SigningKey):
            raise ValueError("No private key available for signing")

        signature = AsymCrypt.sign_message(self.private_key, data)
        return signature

    def verify_signature(self, signature: bytes, data: bytes):
        """Verifies the signature of data using ECDSA if not encryptable."""
        if self.can_encrypt:
            raise AttributeError("Cannot verify with a encryption key")
        elif not isinstance(self.public_key, VerifyKey):
            raise ValueError("No public key available for verification")

        try:
            AsymCrypt.verify_signature(public_key=self.public_key, signature=signature,
                                       data=data)
            return True
        except BadSignatureError:
            return False
