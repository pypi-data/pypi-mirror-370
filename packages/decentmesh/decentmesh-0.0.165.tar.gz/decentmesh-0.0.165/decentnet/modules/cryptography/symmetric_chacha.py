from concurrent.futures.thread import ThreadPoolExecutor
from typing import Optional

from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Random import get_random_bytes
from argon2.low_level import Type, hash_secret

from decentnet.consensus.beam_constants import BEAM_AES_ENCRYPTION_KEY_SIZE


class ChaChaCipher:
    # Class-level constants
    SALT_SIZE = 12  # 12-byte salt
    NONCE_SIZE = 12  # Standard 12-byte nonce
    TAG_SIZE = 16  # Authentication tag size
    DERIVE_KEY_ONCE = True  # Derive the key only once (toggleable)
    CHUNK_SIZE = 1024 * 1024  # 1 MB for a parallelization threshold

    def __init__(self, password: bytes, key_size: int = BEAM_AES_ENCRYPTION_KEY_SIZE,
                 salt: Optional[bytes] = None):
        """
        Initializes the ChaChaCipher with a secure password and optional salt.
        """
        self.password = password
        self.salt = salt if salt is not None else get_random_bytes(self.SALT_SIZE)
        self.key_size = key_size

        # Derive the key only once if DERIVE_KEY_ONCE is True
        if self.DERIVE_KEY_ONCE:
            self.key = self.derive_key(self.password, self.salt)

    def derive_key(self, password: bytes, salt: bytes) -> bytes:
        """
        Derives a cryptographic key using Argon2id with exactly 32 bytes (256 bits).
        """
        derived_key = hash_secret(
            password,
            salt,
            time_cost=1,
            memory_cost=8,
            parallelism=1,
            hash_len=self.key_size,
            type=Type.ID
        )
        return derived_key[:32]

    def encrypt_chunk(self, chunk: bytes, nonce: bytes) -> bytes:
        """
        Encrypts a single chunk using ChaCha20-Poly1305.
        """
        cipher = ChaCha20_Poly1305.new(key=self.key, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(chunk)
        return nonce + tag + ciphertext

    def decrypt_chunk(self, chunk: bytes, key: bytes) -> bytes:
        """
        Decrypts a single chunk using ChaCha20-Poly1305.
        """
        nonce = chunk[:self.NONCE_SIZE]
        tag = chunk[self.NONCE_SIZE:self.NONCE_SIZE + self.TAG_SIZE]
        encrypted_data = chunk[self.NONCE_SIZE + self.TAG_SIZE:]
        cipher = ChaCha20_Poly1305.new(key=key, nonce=nonce)
        return cipher.decrypt_and_verify(encrypted_data, tag)

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypts the plaintext using ChaCha20-Poly1305.
        The output includes salt, nonce, tag, and ciphertext.
        Parallelizes the process if data is larger than CHUNK_SIZE.
        """
        if len(plaintext) <= self.CHUNK_SIZE:
            nonce = get_random_bytes(self.NONCE_SIZE)
            return self.salt + self.encrypt_chunk(plaintext, nonce)

        # Split data into chunks and process in parallel
        chunks = [plaintext[i:i + self.CHUNK_SIZE] for i in range(0, len(plaintext), self.CHUNK_SIZE)]
        with ThreadPoolExecutor() as executor:
            nonces = [get_random_bytes(self.NONCE_SIZE) for _ in chunks]
            encrypted_chunks = list(executor.map(self.encrypt_chunk, chunks, nonces))
        return self.salt + b"".join(encrypted_chunks)

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypts the ciphertext using ChaCha20-Poly1305.
        Parallelizes the process if data is larger than CHUNK_SIZE.
        """
        salt = ciphertext[:self.SALT_SIZE]
        encrypted_data = ciphertext[self.SALT_SIZE:]

        # Derive key if necessary
        key = self.key if self.DERIVE_KEY_ONCE else self.derive_key(self.password, salt)

        # Check if data is small enough for single decryption
        if len(encrypted_data) <= self.CHUNK_SIZE + self.NONCE_SIZE + self.TAG_SIZE:
            return self.decrypt_chunk(encrypted_data, key)

        # Split encrypted data into chunks and process in parallel
        chunk_size = self.CHUNK_SIZE + self.NONCE_SIZE + self.TAG_SIZE
        chunks = [encrypted_data[i:i + chunk_size] for i in range(0, len(encrypted_data), chunk_size)]
        with ThreadPoolExecutor() as executor:
            decrypted_chunks = list(executor.map(self.decrypt_chunk, chunks, [key] * len(chunks)))
        return b"".join(decrypted_chunks)
