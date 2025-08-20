import concurrent.futures
import struct
import warnings
from typing import Optional

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from argon2.low_level import hash_secret

from decentnet.consensus.beam_constants import (BEAM_AES_ENCRYPTION_KEY_SIZE,
                                                DEFAULT_AES_GCM_NONCE_SIZE,
                                                DEFAULT_AES_GCM_TAG_SIZE,
                                                KEY_DERIVE_TIME_COST, KEY_DERIVE_MEM_COST,
                                                KEY_DERIVE_PARALLELISM_COST, KEY_DERIVE_ARGON_TYPE,
                                                AES_FRAME_SIZE, DEFAULT_AES_SALT)


class AESCipher:
    def __init__(self, password: bytes, key_size: int = BEAM_AES_ENCRYPTION_KEY_SIZE,
                 salt: Optional[bytes] = None):
        """
        Initializes the AESCipher with key reuse, nonce optimization, and optional salt.
        Warns if AES-NI is not enabled.
        """
        if key_size not in (128, 192, 256):
            raise ValueError("Key size must be 128, 192, or 256 bits.")

        self.password = password
        self.key_size = key_size
        self.salt = salt if salt is not None else DEFAULT_AES_SALT
        self.key = AESCipher.derive_key(password, self.salt, key_size)  # Precompute key

        if not AESCipher.is_aes_ni_enabled():
            warnings.warn(
                "AES-NI hardware acceleration is not enabled. "
                "Performance may be suboptimal. Ensure your environment supports it."
            )

    @staticmethod
    def derive_key(password: bytes, salt: bytes, key_length: int) -> bytes:
        """
        Derives a cryptographic key using Argon2 with optimized parameters.
        """
        return hash_secret(
            password,
            salt,
            time_cost=KEY_DERIVE_TIME_COST,  # Lower time cost for faster derivation
            memory_cost=KEY_DERIVE_MEM_COST,  # Balanced memory usage
            parallelism=KEY_DERIVE_PARALLELISM_COST,  # Single-threaded for simplicity
            hash_len=key_length // 8,
            type=KEY_DERIVE_ARGON_TYPE  # Argon2id
        )

    @staticmethod
    def is_aes_ni_enabled() -> bool:
        """
        Checks if AES-NI is enabled on the system.
        """
        try:
            with open("/proc/cpuinfo", "r") as cpuinfo:
                return "aes" in cpuinfo.read()
        except FileNotFoundError:
            return True  # Assume AES-NI is available if /proc/cpuinfo is inaccessible

    def encrypt_chunk(self, chunk: bytes) -> bytes:
        # Frame: [ct_len(4B) | nonce | ciphertext]
        key = self.key[: self.key_size // 8]
        nonce = get_random_bytes(DEFAULT_AES_GCM_NONCE_SIZE)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=DEFAULT_AES_GCM_TAG_SIZE, use_aesni=True)
        ct = cipher.encrypt(chunk)
        return struct.pack(">I", len(ct)) + nonce + ct

    def decrypt_chunk(self, chunk: bytes) -> bytes:
        # Expects: [ct_len(4B) | nonce | ciphertext]
        n = DEFAULT_AES_GCM_NONCE_SIZE
        if len(chunk) < AES_FRAME_SIZE + n + 1:
            raise ValueError("Ciphertext too short for framed nonce header.")
        mv = memoryview(chunk)
        ct_len = struct.unpack_from(">I", mv, 0)[0]
        if len(mv) != AES_FRAME_SIZE + n + ct_len or ct_len < 1:
            raise ValueError("Framed chunk length mismatch.")
        nonce = mv[AES_FRAME_SIZE:AES_FRAME_SIZE + n]
        ct = mv[AES_FRAME_SIZE + n:]
        key = self.key[: self.key_size // 8]
        cipher = AES.new(key, AES.MODE_GCM, nonce=bytes(nonce), mac_len=DEFAULT_AES_GCM_TAG_SIZE,
                         use_aesni=True)
        return cipher.decrypt(ct)  # no verify by your choice

    def encrypt(self, plaintext: bytes, chunk_size: int = 1024 * 1024) -> bytes:
        """
        Split plaintext into <=chunk_size pieces, encrypt each via encrypt_chunk(),
        and concatenate framed chunks. Parallelize only if len(plaintext) > chunk_size.
        """
        if len(plaintext) <= chunk_size:
            return self.encrypt_chunk(plaintext)

        # slice plaintext into fixed-size pieces for parallel encrypt
        parts = [plaintext[i:i + chunk_size] for i in range(0, len(plaintext), chunk_size)]
        with concurrent.futures.ThreadPoolExecutor() as ex:
            encrypted_parts = list(ex.map(self.encrypt_chunk, parts))
        return b"".join(encrypted_parts)

    def decrypt(self, encrypted_data: bytes,
                chunk_size: int = 1024 * 1024 + DEFAULT_AES_GCM_NONCE_SIZE + DEFAULT_AES_GCM_TAG_SIZE) -> bytes:
        """
        Parse frames [ct_len(4B)|nonce|ciphertext] and decrypt each with decrypt_chunk().
        Use chunk_size as a threshold: if total size <= chunk_size, decrypt sequentially;
        otherwise, decrypt frames in parallel.
        """
        n = DEFAULT_AES_GCM_NONCE_SIZE
        mv = memoryview(encrypted_data)
        frames = []

        i = 0
        L = len(mv)
        while i < L:
            if i + AES_FRAME_SIZE + n > L:
                raise ValueError("Truncated chunk header.")
            ct_len = struct.unpack_from(">I", mv, i)[0]
            if ct_len < 1:
                raise ValueError("Invalid ciphertext length.")
            frame_len = AES_FRAME_SIZE + n + ct_len
            if i + frame_len > L:
                raise ValueError("Truncated chunk data.")
            frames.append(mv[i:i + frame_len].tobytes())
            i += frame_len

        if len(encrypted_data) <= chunk_size or len(frames) == 1:
            # small payload: sequential
            return b"".join(self.decrypt_chunk(f) for f in frames)

        # large payload: parallel per frame
        with concurrent.futures.ThreadPoolExecutor() as ex:
            parts = list(ex.map(self.decrypt_chunk, frames))
        return b"".join(parts)
