import unittest

from decentnet.modules.cryptography.asymmetric import AsymCrypt
from decentnet.modules.key_util.key_manager import KeyManager


class TestKeyManagerDatabase(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Setup before each test, you can reset the database or set test data here
        # Optionally, ensure the database is clean
        pass

    async def asyncTearDown(self):
        # Clean up after each test if necessary
        await KeyManager.clear_db()

    async def test_save_and_retrieve_from_db(self):
        # Test data

        private_key, o_public_key = KeyManager.generate_singing_key_pair()
        public_key = AsymCrypt.verifying_key_to_string(o_public_key)

        private_key = KeyManager.key_to_base64(private_key)

        description = "Test Key"
        can_encrypt = False
        alias = "test_alias"

        # Save the key pair to the database
        key_id = await KeyManager.save_to_db(private_key, public_key, description, can_encrypt, alias)

        self.assertTrue(key_id)
        # Verify that the key pair was saved by retrieving it
        retrieved_private_key, retrieved_public_key = await KeyManager.retrieve_ssh_key_pair_from_db(key_id,
                                                                                                     can_encrypt)

        # Assertions to verify that the saved and retrieved data match
        self.assertEqual(AsymCrypt.verifying_key_to_string(retrieved_public_key), public_key)


if __name__ == '__main__':
    unittest.main()
