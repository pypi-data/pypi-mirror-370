import time
import unittest

from decentnet.modules.compression.hbw_wrapper import CompressionHBW


class TestCompressionWrapperPerformance(unittest.TestCase):

    def test_compression_performance(self):
        original_data = b'"activities": ["login", "update_profile", "logout"]}' * 10 ** 4  # 1 MB of repetitive data, adjust as needed

        # Define the ranges for compression levels and block sizes
        compression_levels = range(5, 21)  # Compression levels from 5 to 20
        block_sizes = [64 * 1024, 128 * 1024, 256 * 1024]  # Block sizes: 64KB, 128KB, 256KB

        for level in compression_levels:
            for block_size in block_sizes:
                with self.subTest(compression_level=level, block_size=block_size):
                    # Measure compression time
                    start_time = time.time()
                    compressed_data, data_size = CompressionHBW.compress_lz4(original_data, level)
                    compression_time = time.time() - start_time

                    # Ensure compression was successful
                    self.assertIsNotNone(compressed_data)
                    self.assertGreater(len(compressed_data), 0)

                    # Measure decompression time
                    start_time = time.time()
                    decompressed_data = CompressionHBW.decompress_lz4(compressed_data)
                    decompression_time = time.time() - start_time

                    # Ensure decompression was successful and data integrity is maintained
                    self.assertEqual(original_data, decompressed_data)

                    # Calculate compression ratio
                    compression_ratio = len(compressed_data) / len(original_data)

                    # Print performance metrics
                    print(f"Level: {level}, Block Size: {block_size // 1024} KB, "
                          f"Compression Time: {compression_time:.6f}s, "
                          f"Decompression Time: {decompression_time:.6f}s, "
                          f"Compression Ratio: {compression_ratio:.4f}")


if __name__ == '__main__':
    unittest.main()
