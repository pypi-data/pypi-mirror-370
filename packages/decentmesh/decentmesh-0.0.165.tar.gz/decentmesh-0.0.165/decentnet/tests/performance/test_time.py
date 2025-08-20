import time
import unittest
from datetime import datetime


class TestTimestampPerformance(unittest.TestCase):

    def setUp(self):
        self.iterations = 10000000  # Define iterations as a class attribute

    def test_datetime_now_timestamp(self):
        block_timestamp = datetime.now().timestamp()

        start_time = time.time()
        for _ in range(self.iterations):
            (datetime.now().timestamp() - block_timestamp) * 1000
        end_time = time.time()

        duration = end_time - start_time
        print(f"datetime.now().timestamp() method took {duration:.6f} seconds")

    def test_time_time(self):
        block_timestamp = time.time()

        start_time = time.time()
        for _ in range(self.iterations):
            (time.time() - block_timestamp) * 1000
        end_time = time.time()

        duration = end_time - start_time
        print(f"time.time() method took {duration:.6f} seconds")

    def test_time_monotonic(self):
        block_timestamp = time.time()

        start_time = time.time()
        for _ in range(self.iterations):
            (time.time() - block_timestamp) * 1000
        end_time = time.time()

        duration = end_time - start_time
        print(f"time.time() method took {duration:.6f} seconds")

    def test_time_perf_counter(self):
        block_timestamp = time.perf_counter()

        start_time = time.time()
        for _ in range(self.iterations):
            (time.perf_counter() - block_timestamp) * 1000
        end_time = time.time()

        duration = end_time - start_time
        print(f"time.perf_counter() method took {duration:.6f} seconds")


if __name__ == "__main__":
    unittest.main()
