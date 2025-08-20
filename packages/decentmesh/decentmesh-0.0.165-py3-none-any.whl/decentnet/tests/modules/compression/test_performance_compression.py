import math
import random
import string
import timeit
import unittest

from decentnet.modules.compression.zl_wrapper import CompressionSBW


def generate_random_data(size):
    # Generate random data with the specified size
    return bytes(''.join(random.choices(string.ascii_letters + string.digits, k=size)),
                 'utf-8')


def format_size(size_bytes):
    # Adapted from: https://stackoverflow.com/a/1094933/9667816
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    size = round(size_bytes / p, 2)
    return f"{size} {size_name[i]}"


class CompressionPerformanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = generate_random_data(
            random.randint(1000, 10000))


    def test_fast_compression_performance(self):
        def run_fast_compression():
            compressed_data = CompressionSBW.compress_zlib(self.data, level=9)
            original_size = len(self.data)
            compressed_size = len(compressed_data)
            saved_bytes = original_size - compressed_size
            print("Fast Compression: Compressed", format_size(original_size), "to",
                  format_size(compressed_size) + ". Saved",
                  format_size(saved_bytes) + ".")

        fast_time = timeit.timeit(run_fast_compression, number=1)

        print("Fast Compression Time:", fast_time * 1000, "milliseconds")


if __name__ == '__main__':
    unittest.main()
