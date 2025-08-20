import unittest

from decentnet.modules.cryptography.asym_man import AsymmetricManager
from decentnet.modules.cryptography.asymmetric import AsymCrypt


class TestAsymmetricManager(unittest.TestCase):
    def test_encryption(self):
        # Generate key pair for encryption using AsymCrypt
        private_key, public_key = AsymCrypt.generate_key_pair_encryption()

        self.assertTrue(AsymCrypt.check_encryption_key(public_key),
                        "This is not encryption key")

        # Create an instance of AsymmetricManager for encryption
        manager = AsymmetricManager(public_key=public_key, private_key=private_key,
                                    can_encrypt=True)

        # Test encryption and decryption
        original_message = b"Hello, world!"
        encrypted = manager.encrypt_message(original_message)
        decrypted = manager.decrypt_message(encrypted)
        self.assertEqual(original_message, decrypted)

    def test_signing(self):
        # Generate key pair for signing using AsymCrypt
        private_key, public_key = AsymCrypt.generate_key_pair_signing()
        self.assertFalse(AsymCrypt.check_encryption_key(public_key),
                         "This is an encryption key not signing key")
        # Create an instance of AsymmetricManager for signing
        manager = AsymmetricManager(private_key=private_key, public_key=public_key)

        # Test signing and verification
        message = b"Hello, world!"
        signature = manager.sign_message(message)
        self.assertTrue(manager.verify_signature(signature, message))

    def test_failure_cases(self):
        # Test cases where incorrect methods are called
        manager = AsymmetricManager()

        # Attempt to encrypt without encryption capabilities
        with self.assertRaises(AttributeError):
            manager.encrypt_message(b"test")

        # Attempt to decrypt without decryption capabilities
        with self.assertRaises(AttributeError):
            manager.decrypt_message(b"test")

        # Attempt to sign without signing capabilities
        with self.assertRaises(ValueError):
            manager.sign_message(b"test")

        # Attempt to verify without verification capabilities
        with self.assertRaises(ValueError):
            manager.verify_signature(b"test", b"test")


if __name__ == '__main__':
    unittest.main()
