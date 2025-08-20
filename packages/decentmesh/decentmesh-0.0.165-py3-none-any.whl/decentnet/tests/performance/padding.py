import struct
import timeit
import unittest

import numpy as np
from Crypto.Util.Padding import pad, unpad

HASH_LEN = 32  # Example hash length


class TestPaddingPerformance(unittest.TestCase):

    def setUp(self):
        self.previous_hash = b'\x01\x02\x03\x04'  # Example hash with a few non-zero bytes

    def test_lstrip_performance(self):
        def lstrip_unpadding():
            padded = self.previous_hash.rjust(HASH_LEN, b'\x00')
            return padded.lstrip(b'\x00') or None

        time_taken = timeit.timeit(lstrip_unpadding, number=1000000)
        print(f"lstrip unpadding: {time_taken:.6f} seconds")

    def test_struct_performance(self):
        def struct_padding():
            return struct.pack(f'>{HASH_LEN}s', self.previous_hash)

        def struct_unpadding():
            padded = struct.pack(f'>{HASH_LEN}s', self.previous_hash)
            return struct.unpack(f'>{HASH_LEN}s', padded)[0].rstrip(b'\x00') or None

        time_taken_padding = timeit.timeit(struct_padding, number=1000000)
        time_taken_unpadding = timeit.timeit(struct_unpadding, number=1000000)
        print(f"struct padding: {time_taken_padding:.6f} seconds")
        print(f"struct unpadding: {time_taken_unpadding:.6f} seconds")

    def test_numpy_performance(self):
        def numpy_padding():
            previous_hash_np = np.frombuffer(self.previous_hash, dtype=np.uint8)
            padded_previous_hash = np.pad(previous_hash_np, (HASH_LEN - len(previous_hash_np), 0), 'constant',
                                          constant_values=(0))
            return padded_previous_hash.tobytes()

        def numpy_unpadding():
            previous_hash_np = np.frombuffer(self.previous_hash.rjust(HASH_LEN, b'\x00'), dtype=np.uint8)
            first_non_zero_index = np.argmax(previous_hash_np > 0)
            return previous_hash_np[first_non_zero_index:].tobytes() or None

        time_taken_padding = timeit.timeit(numpy_padding, number=1000000)
        time_taken_unpadding = timeit.timeit(numpy_unpadding, number=1000000)
        print(f"numpy padding: {time_taken_padding:.6f} seconds")
        print(f"numpy unpadding: {time_taken_unpadding:.6f} seconds")

    def test_pycryptodome_performance(self):
        def pycryptodome_padding():
            return pad(self.previous_hash, HASH_LEN, style='iso7816')

        def pycryptodome_unpadding():
            padded = pad(self.previous_hash, HASH_LEN, style='iso7816')
            return unpad(padded, HASH_LEN, style='iso7816')

        time_taken_padding = timeit.timeit(pycryptodome_padding, number=1000000)
        time_taken_unpadding = timeit.timeit(pycryptodome_unpadding, number=1000000)
        print(f"PyCryptodome padding: {time_taken_padding:.6f} seconds")
        print(f"PyCryptodome unpadding: {time_taken_unpadding:.6f} seconds")


if __name__ == '__main__':
    unittest.main()
