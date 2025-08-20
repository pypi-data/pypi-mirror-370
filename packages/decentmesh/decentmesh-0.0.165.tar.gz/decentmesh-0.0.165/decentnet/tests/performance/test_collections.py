import time
import unittest
from collections import deque
from multiprocessing import Queue as MPQueue
from queue import SimpleQueue


class TestQueueVsListPerformance(unittest.TestCase):

    def setUp(self):
        self.num_elements = 10 ** 6  # 1 million elements for the test

    def test_list_append_performance(self):
        lst = []
        start_time = time.time()

        for i in range(self.num_elements):
            lst.append(i)

        elapsed_time = time.time() - start_time
        print(f"List: Time to append {self.num_elements} elements: {elapsed_time:.4f} seconds")

    def test_deque_append_performance(self):
        dq = deque()
        start_time = time.time()

        for i in range(self.num_elements):
            dq.append(i)

        elapsed_time = time.time() - start_time
        print(f"Deque: Time to append {self.num_elements} elements: {elapsed_time:.4f} seconds")

    def test_multiprocessing_queue_performance(self):
        mpq = MPQueue()
        start_time = time.time()

        for i in range(self.num_elements):
            mpq.put(i)

        elapsed_time = time.time() - start_time
        print(
            f"Multiprocessing Queue: Time to insert {self.num_elements} elements: {elapsed_time:.4f} seconds")

    def test_simplequeue_performance(self):
        sq = SimpleQueue()
        start_time = time.time()

        for i in range(self.num_elements):
            sq.put(i)

        elapsed_time = time.time() - start_time
        print(f"SimpleQueue: Time to insert {self.num_elements} elements: {elapsed_time:.4f} seconds")


if __name__ == '__main__':
    unittest.main()
