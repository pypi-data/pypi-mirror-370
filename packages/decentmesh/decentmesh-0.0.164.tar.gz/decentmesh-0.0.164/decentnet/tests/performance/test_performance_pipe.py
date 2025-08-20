import random
import time
import unittest
from multiprocessing import Manager, Pipe, Process

from decentnet.consensus.block_sizing import MAXIMUM_BLOCK_SIZE


def generate_messages(num_messages: int) -> list:
    """
    Generate random messages beforehand, providing verbose output for each message.

    Args:
        num_messages (int): The number of random messages to generate.

    Returns:
        list: A list of random byte messages.
    """
    messages = []
    for i in range(num_messages):
        size = random.randint(1, MAXIMUM_BLOCK_SIZE)
        message = random.randbytes(size)
        messages.append(message)

        # Verbose output for each message
        print(f"Generated message {i + 1}/{num_messages} - Size: {size} bytes")

    print(f"Total {num_messages} messages generated.")
    return messages


def consumer_process(pipe, num_messages):
    """
    Function for consumer process to consume messages.

    Args:
        pipe: The read end of the pipe.
        num_messages: Number of messages to consume.
    """
    consumer_conn = pipe[0]  # The consumer reads from pipe[0]
    for _ in range(num_messages):
        consumer_conn.recv()


def producer_process(pipe, messages):
    """
    Function for producer process to publish pre-generated messages.

    Args:
        pipe: The write end of the pipe.
        messages: List of pre-generated messages.
    """
    producer_conn = pipe[1]  # The producer writes to pipe[1]
    for message in messages:
        producer_conn.send(message)  # Send the message through the pipe


class PerformanceTest(unittest.TestCase):

    def test_performance(self):
        """
        Test the performance of the Producer/Consumer message passing using pipes.
        Measures both the latency (time it takes for a message to reach the consumer)
        and the throughput (messages per second).
        """

        # Number of messages to test throughput
        num_messages = 1000
        print("Generating messages...")
        manager = Manager()
        messages = manager.list(generate_messages(num_messages))

        # Create a Pipe for communication
        pipe = Pipe()

        # Start the timer for latency and throughput measurement
        start_time = time.perf_counter_ns()

        # Create consumer and producer processes
        consumer_proc = Process(target=consumer_process, args=(pipe, num_messages))
        producer_proc = Process(target=producer_process, args=(pipe, messages))

        # Start both processes
        consumer_proc.start()
        producer_proc.start()

        # Wait for both processes to finish
        producer_proc.join()
        consumer_proc.join()

        # End time after processes complete
        end_time = time.perf_counter_ns()

        # Calculate the time taken and throughput
        total_time = end_time - start_time

        # Latency per message (in nanoseconds)
        latency_per_message = total_time / num_messages

        # Throughput calculation: number of messages per second
        throughput = num_messages / (total_time / 1_000_000_000)

        # Output in milliseconds (convert from nanoseconds)
        print(f"Total time for {num_messages} messages: {total_time / 1_000_000:.6f} ms")
        print(f"Average latency per message: {latency_per_message / 1_000_000:.6f} ms")
        print(f"Throughput: {throughput:.6f} messages per second")


if __name__ == '__main__':
    unittest.main()
