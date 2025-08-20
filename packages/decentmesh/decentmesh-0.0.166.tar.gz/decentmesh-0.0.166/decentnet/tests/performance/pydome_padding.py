import timeit
import unittest

from Crypto.Util.Padding import pad, unpad


class TestPaddingPerformance(unittest.TestCase):

    def setUp(self):
        # Example data and block size
        self.data = b"This is some data"  # Larger dataset for more realistic performance testing
        self.block_size = 32
        self.iterations = 1000000  # Number of iterations to run each test

    def measure_time(self, func):
        return timeit.timeit(func, number=self.iterations)

    def test_padding_performance(self):
        # Measure PKCS7 padding and unpadding together
        pkcs7_time = self.measure_time(
            lambda: unpad(pad(self.data, self.block_size, style='pkcs7'), self.block_size, style='pkcs7')
        )

        # Measure ANSI X.923 padding and unpadding together
        x923_time = self.measure_time(
            lambda: unpad(pad(self.data, self.block_size, style='x923'), self.block_size, style='x923')
        )

        # Measure ISO 7816-4 padding and unpadding together
        iso7816_time = self.measure_time(
            lambda: unpad(pad(self.data, self.block_size, style='iso7816'), self.block_size, style='iso7816')
        )

        # Aggregate results
        results = [
            ('PKCS7 Padding/Unpadding', pkcs7_time),
            ('ANSI X.923 Padding/Unpadding', x923_time),
            ('ISO 7816-4 Padding/Unpadding', iso7816_time),
        ]

        # Sort results by combined time (ascending)
        results.sort(key=lambda x: x[1])

        # Print the ledger
        print("\nPerformance Ledger (from fastest to slowest):")
        for method, time_taken in results:
            print(f"{method}: {time_taken:.6f} seconds")


if __name__ == '__main__':
    unittest.main()
