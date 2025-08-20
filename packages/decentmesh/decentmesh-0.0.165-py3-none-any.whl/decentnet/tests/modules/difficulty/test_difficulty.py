import unittest

from decentnet.consensus.block_sizing import MERGED_DIFFICULTY_BYTE_LEN
from decentnet.modules.pow.difficulty import Difficulty


class TestDifficultyConversion(unittest.TestCase):
    def test_bytes_conversion_round_trip(self):
        test_cases = [
            (1, 16, 2, 255, 32),
            (10, 1024, 20, 8, 64),
            (0, 32, 1, 1, 1),
            (255, 2048, 255, 255, 255)
        ]

        for t_cost, m_cost, p_cost, n_bits, hash_len_chars in test_cases:
            with self.subTest(t_cost=t_cost, m_cost=m_cost, p_cost=p_cost, n_bits=n_bits,
                              hash_len_chars=hash_len_chars):
                original = Difficulty(t_cost, m_cost, p_cost, n_bits, hash_len_chars, 12)
                converted_bytes = original.to_bytes()
                reconstructed = Difficulty.from_bytes(converted_bytes)

                self.assertEqual(original, reconstructed)

    def test_difficulty_size(self):
        test_cases = [
            (1, 16, 2, 255, 32),
            (10, 1024, 20, 8, 64),
            (0, 32, 1, 1, 1),
            (255, 2048, 255, 255, 255)
        ]

        for t_cost, m_cost, p_cost, n_bits, hash_len_chars in test_cases:
            with self.subTest(t_cost=t_cost, m_cost=m_cost, p_cost=p_cost, n_bits=n_bits,
                              hash_len_chars=hash_len_chars):
                original = Difficulty(t_cost, m_cost, p_cost, n_bits, hash_len_chars, 12)
                converted_bytes = original.to_bytes()
                size = len(converted_bytes)
                self.assertEqual(size, MERGED_DIFFICULTY_BYTE_LEN)


if __name__ == '__main__':
    unittest.main()
