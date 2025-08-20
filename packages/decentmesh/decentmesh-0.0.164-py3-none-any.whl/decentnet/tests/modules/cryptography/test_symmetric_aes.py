import unittest
from time import perf_counter

from decentnet.modules.cryptography.symmetric_aes import AESCipher


class TestAESCipher(unittest.TestCase):

    def test_encrypt_decrypt_with_different_key_sizes(self):
        for key_size in [128, 192, 256]:
            with self.subTest(key_size=key_size):
                password = "testpassword".encode()
                plaintext = b"This is a test message."
                cipher = AESCipher(password=password, key_size=key_size)

                # Encrypt the plaintext
                encrypted_text = cipher.encrypt(plaintext)

                # Decrypt the encrypted text
                decrypted_text = cipher.decrypt(encrypted_text)

                # Assert that the decrypted text is the same as the original plaintext
                self.assertEqual(decrypted_text, plaintext)

    def test_invalid_key_size(self):
        with self.assertRaises(ValueError):
            AESCipher(b"array", 64)  # An unsupported key size

    def test_performance(self):
        password = "testpassword".encode()
        key_size = 256
        plaintext = b"A" * (4 * 1024 * 1024)  # 4 MB of data
        cipher = AESCipher(password=password, key_size=key_size)

        num_runs = 30  # Number of runs to average
        encryption_times = []
        decryption_times = []

        for _ in range(num_runs):
            # Measure encryption performance
            start_time = perf_counter()
            encrypted_text = cipher.encrypt(plaintext)
            encryption_times.append((perf_counter() - start_time) * 1000)  # Convert to milliseconds

            # Measure decryption performance
            start_time = perf_counter()
            decrypted_text = cipher.decrypt(encrypted_text)
            decryption_times.append((perf_counter() - start_time) * 1000)  # Convert to milliseconds

            # Assert decryption matches original plaintext
            self.assertEqual(decrypted_text, plaintext)

        avg_encrypt_time = sum(encryption_times) / num_runs
        avg_decrypt_time = sum(decryption_times) / num_runs

        print(f"Average encryption time over {num_runs} runs: {avg_encrypt_time:.2f} ms.")
        print(f"Average decryption time over {num_runs} runs: {avg_decrypt_time:.2f} ms.")
        self.assertLess(avg_encrypt_time, 10)
        self.assertLess(avg_decrypt_time, 10)

    def test_performance_small_data(self):
        """
        Measures the performance of encryption and decryption with smaller data (128 KB).
        """
        password = b"testpassword"
        key_size = 256
        plaintext = b"A" * (2 * 1024)  # 2 KB of data
        cipher = AESCipher(password=password, key_size=key_size)

        num_runs = 10  # Number of runs to average
        encryption_times = []
        decryption_times = []

        for _ in range(num_runs):
            # Measure encryption performance
            start_time = perf_counter()
            encrypted_text = cipher.encrypt(plaintext)
            encryption_times.append((perf_counter() - start_time) * 1000)  # Convert to milliseconds

            # Measure decryption performance
            start_time = perf_counter()
            decrypted_text = cipher.decrypt(encrypted_text)
            decryption_times.append((perf_counter() - start_time) * 1000)  # Convert to milliseconds

            # Assert decryption matches original plaintext
            self.assertEqual(decrypted_text, plaintext)

        avg_encrypt_time = sum(encryption_times) / num_runs
        avg_decrypt_time = sum(decryption_times) / num_runs

        print(f"Average encryption time for 2 KB over {num_runs} runs: {avg_encrypt_time:.2f} ms.")
        print(f"Average decryption time for 2 KB over {num_runs} runs: {avg_decrypt_time:.2f} ms.")

        self.assertLess(avg_encrypt_time, 0.1)
        self.assertLess(avg_decrypt_time, 0.1)



if __name__ == '__main__':
    unittest.main()
