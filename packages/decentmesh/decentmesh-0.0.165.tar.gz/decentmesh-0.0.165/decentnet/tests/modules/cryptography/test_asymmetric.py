import unittest

from decentnet.modules.cryptography.asymmetric import AsymCrypt
from decentnet.modules.serializer.serializer import Serializer


class TestAsymCrypt(unittest.TestCase):
    def setUp(self):
        # Generate keys for each test case
        self.private_key_sign, self.public_key_sign = AsymCrypt.generate_key_pair_signing()
        self.private_key_enc, self.public_key_enc = AsymCrypt.generate_key_pair_encryption()
        self.test_message = b"test_message"

    def test_serialize_deserialize(self):
        signature = b"test_signature"
        encrypted_data = b"test_encrypted_data"

        serialized = Serializer.serialize_data(self.public_key_sign, signature,
                                               encrypted_data)
        deserialized = Serializer.deserialize_data(serialized)

        self.assertEqual(deserialized['sig'], signature)
        self.assertEqual(deserialized['data'], encrypted_data)

    def test_encryption_decryption(self):
        encrypted_data = AsymCrypt.encrypt_message(self.public_key_enc, self.test_message)
        decrypted_data = AsymCrypt.decrypt_message(self.private_key_enc, encrypted_data)

        self.assertEqual(decrypted_data, self.test_message)

    def test_sign_verify(self):
        private_key, public_key = AsymCrypt.generate_key_pair_signing()
        signature = AsymCrypt.sign_message(private_key, self.test_message)
        verified = AsymCrypt.verify_signature(public_key=public_key, signature=signature,
                                              data=self.test_message)

        self.assertTrue(verified)


if __name__ == '__main__':
    unittest.main()
