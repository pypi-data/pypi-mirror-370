import time
import unittest

from decentnet.consensus.block_sizing import HASH_LEN
from decentnet.consensus.compress_params import COMPRESSION_LEVEL_LZ4
from decentnet.modules.dynamic_diff.generate import get_difficulty_parameters
from decentnet.modules.hash_type.hash_type import MemoryHash
from decentnet.modules.pow.difficulty import Difficulty
from decentnet.modules.pow.pow import PoW


@unittest.skip("Not Implemented")
class TestArgon2Parameters(unittest.TestCase):

    def test_base_parameters(self):
        """ Test if the base parameters are correct for index 0 """
        expected = {
            "Memory Cost (KB)": 1024,
            "Time Cost (Iterations)": 1,
            "Parallelism": 2,
            "Zero Bits": 1
        }
        self.assertEqual(get_difficulty_parameters(0), expected)

    def test_incremented_parameters(self):
        """ Test if the parameters increment correctly """
        # Test for index 1
        expected_index_1 = {
            "Memory Cost (KB)": 2048,
            "Time Cost (Iterations)": 2,
            "Parallelism": 2,
            "Zero Bits": 2
        }
        self.assertEqual(get_difficulty_parameters(1), expected_index_1)

        # Test for index 5
        expected_index_5 = {
            "Memory Cost (KB)": 6144,
            "Time Cost (Iterations)": 6,
            "Parallelism": 2,
            "Zero Bits": 6
        }
        self.assertEqual(get_difficulty_parameters(5), expected_index_5)

    def test_high_index(self):
        """ Test if the function handles high indices correctly """
        index = 100
        expected = {
            "Memory Cost (KB)": 1024 + 1024 * index,
            "Time Cost (Iterations)": 1 + index,
            "Parallelism": 2,
            "Zero Bits": 1 + index
        }
        self.assertEqual(get_difficulty_parameters(index), expected)

    def test_linear_time_increment(self):
        """ Test if the time cost increases linearly with the index """
        previous_time_cost = None
        consistent_increment = True
        increment = None

        for index in range(1, 99999999):  # Testing for indices 1 to 10
            tolerance_percentage = 100
            pa = get_difficulty_parameters(index)
            diff = Difficulty(pa["t"], pa["m"], pa["p"], pa["b"], HASH_LEN, COMPRESSION_LEVEL_LZ4)
            pw = MemoryHash(diff, bytes(0x86))
            start_time = time.time()
            PoW.compute(pw, diff)
            end_time = time.time()

            current_time_cost = end_time - start_time
            print(
                f"Difficulty: {diff} Index: {index}, Execution Time: {current_time_cost} seconds")

            if previous_time_cost is not None:
                current_increment = current_time_cost - previous_time_cost

                if not increment:
                    increment = current_increment
                else:
                    # Calculate the acceptable range based on the tolerance
                    lower_bound = increment * (1 - tolerance_percentage / increment)
                    upper_bound = increment * (1 + tolerance_percentage / increment)

                    if not (lower_bound <= current_increment <= upper_bound):
                        self.fail(
                            f"Time cost increment is not within the tolerance range at index {index}")

            previous_time_cost = current_time_cost

        self.assertTrue(consistent_increment, "Time cost increment is not linear")


# Running the tests
if __name__ == '__main__':
    unittest.main()
