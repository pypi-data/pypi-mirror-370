import asyncio
import unittest

from decentnet.consensus.metrics_constants import MAX_REQUEST_QUEUE_LEN
from decentnet.modules.req_queue.reques_queue import ReqQueue


class TestReqQueue(unittest.TestCase):

    def setUp(self):
        ReqQueue.init_queue()  # Initialize the queue before each test
        ReqQueue.item_count = 0

    def test_append_function_to_queue_with_modified_len(self):
        # Test with modified queue length
        def test_func():
            pass

        # Test appending the function to the queue
        ReqQueue.append(test_func)
        ReqQueue.append(test_func)

        # Attempt to add another function, which should not append immediately

        # Verify the length and item count in the queue
        self.assertEqual(len(ReqQueue._requeue), 2)
        self.assertEqual(ReqQueue.item_count, 2)

    def test_overflow_discarded(self):
        # Test with modified queue length
        async def test_func():
            pass

        # Fill the queue to its maximum length (2 in this case)
        for _ in range(MAX_REQUEST_QUEUE_LEN):
            ReqQueue.append(asyncio.run(test_func()))

        # Check queue length before adding one more function
        self.assertEqual(len(ReqQueue._requeue), MAX_REQUEST_QUEUE_LEN)
        self.assertEqual(ReqQueue.item_count, MAX_REQUEST_QUEUE_LEN)


        ReqQueue.append(asyncio.run(test_func()))

        if len(ReqQueue._requeue) > MAX_REQUEST_QUEUE_LEN:
            self.fail("Overflowed")


if __name__ == '__main__':
    unittest.main()
