import unittest
from time import perf_counter

from decentnet.modules.cryptography.symmetric_chacha import ChaChaCipher


class TestChaChaCipher(unittest.TestCase):

    def test_encrypt_decrypt(self):
        password = "testpassword".encode()
        plaintext = b"This is a test message."
        cipher = ChaChaCipher(password=password)

        # Encrypt the plaintext
        encrypted_text = cipher.encrypt(plaintext)

        # Decrypt the encrypted text
        decrypted_text = cipher.decrypt(encrypted_text)

        # Assert that the decrypted text is the same as the original plaintext
        self.assertEqual(decrypted_text, plaintext)

    def test_performance(self):
        password = "testpassword".encode()
        plaintext = b"A" * (4 * 1024 * 1024)  # 4 MB of data
        cipher = ChaChaCipher(password=password)

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
        self.assertLess(avg_encrypt_time, 30)
        self.assertLess(avg_decrypt_time, 30)

    def test_performance_small_data(self):
        password = b"testpassword"
        plaintext = b"A" * (2 * 1024)  # 2 KB of data
        cipher = ChaChaCipher(password=password)

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

        self.assertLess(avg_encrypt_time, 2)
        self.assertLess(avg_decrypt_time, 2)

    def test_compromised_data(self):
        password = "testpassword".encode()
        plaintext = b"This is a test message."
        cipher = ChaChaCipher(password=password)

        # Encrypt the plaintext
        encrypted_text = cipher.encrypt(plaintext)

        # Modify the encrypted text to compromise it
        compromised_text = bytearray(encrypted_text)
        compromised_text[-1] ^= 0x01  # Flip the last byte to corrupt the data

        # Decrypting compromised text should raise a ValueError
        with self.assertRaises(ValueError):
            cipher.decrypt(bytes(compromised_text))


if __name__ == '__main__':
    unittest.main()
