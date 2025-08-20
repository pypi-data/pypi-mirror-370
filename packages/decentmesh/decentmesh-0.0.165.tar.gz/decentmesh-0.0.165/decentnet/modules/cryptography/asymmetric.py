import logging
import os

from nacl.exceptions import BadSignatureError
from nacl.public import Box, PrivateKey, PublicKey
from nacl.signing import SigningKey, VerifyKey

from decentnet.consensus.dev_constants import RUN_IN_DEBUG
from decentnet.modules.convert.byte_to_base64_utils import (base64_to_original,
                                                            bytes_to_base64)
from decentnet.modules.logger.log import setup_logger

logger = logging.getLogger(__name__)

setup_logger(RUN_IN_DEBUG, logger)


class AsymCrypt:

    @staticmethod
    def generate_key_pair_encryption() -> [bytes, bytes]:
        """Generate a key pair for encryption using PyNaCl (Curve25519)."""
        private_key = PrivateKey.generate()
        public_key = private_key.public_key
        return private_key.encode(), public_key.encode()

    @staticmethod
    def generate_key_pair_signing() -> [SigningKey, VerifyKey]:
        """Generate a key pair for Ed25519 (replaces ECDSA)."""
        # Generate a private key (SigningKey)
        private_key = SigningKey.generate()

        # Derive the public key from the private key
        public_key = private_key.verify_key

        return private_key, public_key

    @staticmethod
    def check_encryption_key(public_key: bytes):
        try:
            # Ensure public key is a valid NaCl public key
            PublicKey(public_key)
            return True
        except Exception:
            return False

    @staticmethod
    def encrypt_message(public_key: bytes, data: bytes) -> bytes:
        """
        Encrypts data using PyNaCl Box (public-key encryption).
        :param public_key: The recipient's public key (as bytes).
        :param data: The plaintext data to encrypt (as bytes).
        :return: Encrypted data with nonce included.
        """
        recipient_public_key = PublicKey(public_key)

        # Sender uses their own fixed private key (assumed to be managed externally)
        sender_private_key = PrivateKey.generate()  # This can be passed into the function instead
        box = Box(sender_private_key, recipient_public_key)

        # Encrypt the message, including a random nonce
        encrypted = box.encrypt(data, nonce=os.urandom(Box.NONCE_SIZE))

        # Prepend the sender's public key (required for decryption)
        return sender_private_key.public_key.encode() + encrypted

    @staticmethod
    def decrypt_message(private_key: bytes, encrypted_data: bytes) -> bytes:
        """
        Decrypts data using PyNaCl Box (public-key encryption).
        :param private_key: The recipient's private key (as bytes).
        :param encrypted_data: The encrypted data with nonce and sender's public key prepended.
        :return: Decrypted plaintext data.
        """
        # Extract sender's public key (first 32 bytes)
        sender_public_key = PublicKey(encrypted_data[:32])
        encrypted_message = encrypted_data[32:]

        # Use recipient's private key
        recipient_private_key = PrivateKey(private_key)

        # Create a Box with recipient's private key and sender's public key
        box = Box(recipient_private_key, sender_public_key)

        # Decrypt the message
        decrypted_data = box.decrypt(encrypted_message)
        return decrypted_data

    @staticmethod
    def sign_message(private_key: SigningKey, data: bytes) -> bytes:
        """Signs data using Ed25519 (replaces ECDSA)."""
        signature = private_key.sign(data).signature
        return signature

    @staticmethod
    def verify_signature(*, public_key: VerifyKey, signature: bytes, data: bytes) -> bool:
        """Verifies the signature of data using Ed25519."""
        try:
            public_key.verify(data, signature)
            return True
        except BadSignatureError:
            return False

    @staticmethod
    def key_pair_from_private_key_base64(private_key: str, can_encrypt: bool) -> tuple[
                                                                                     SigningKey, VerifyKey] | \
                                                                                 tuple[bytes, bytes]:
        """
        Returns an Object key pair from base64 str.
        :param private_key:
        :param can_encrypt:
        :return: Private Key Object, Public Key object.
        """
        if not can_encrypt:
            private_key = SigningKey(base64_to_original(private_key))
            public_key = private_key.verify_key
            return private_key, public_key
        else:
            pk_bytes = base64_to_original(private_key)
            private_key = PrivateKey(pk_bytes)
            public_key = private_key.public_key
            return private_key.encode(), public_key.encode()

    @staticmethod
    def public_key_from_base64(public_key: str, can_encrypt: bool) -> VerifyKey | bytes:
        """
        Returns Object key from base64 str.
        :param public_key:
        :param can_encrypt:
        :return: Private Key Object, Public Key object.
        """
        if not can_encrypt:
            return VerifyKey(base64_to_original(public_key))
        else:
            pk_bytes = base64_to_original(public_key)
            return PublicKey(pk_bytes).encode()

    @staticmethod
    def encryption_key_to_base64(key: bytes) -> str:
        """
        Converts bytes of public or private key to base64.
        :param key:
        :return:
        """
        return bytes_to_base64(key)

    @staticmethod
    def verifying_key_to_string(key: VerifyKey) -> str:
        """
        Converts a verification key into string base64.
        :param key:
        :return:
        """
        return bytes_to_base64(key.encode())

    @staticmethod
    def verifying_key_from_string(key: str) -> VerifyKey:
        return VerifyKey(base64_to_original(key))
