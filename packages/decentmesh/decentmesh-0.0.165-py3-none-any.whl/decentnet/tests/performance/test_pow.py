import ctypes
import timeit

from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE

PyLong_AsByteArray = ctypes.pythonapi._PyLong_AsByteArray
PyLong_AsByteArray.argtypes = [ctypes.py_object,
                               ctypes.POINTER(ctypes.c_uint8),
                               ctypes.c_size_t,
                               ctypes.c_int,
                               ctypes.c_int]


# Original int_to_bytes function
def int_to_bytes_original(num: int, buffer=None):
    byte_length = num.bit_length() // 8 + 1
    if buffer is None or len(buffer) < byte_length:
        buffer = (ctypes.c_uint8 * byte_length)()
    PyLong_AsByteArray(num, buffer, byte_length, 0, 1)
    return bytes(buffer)


# Optimized int_to_bytes function
def int_to_bytes_optimized(num: int, buffer=None):
    byte_length = (num.bit_length() + 7) // 8
    if buffer is None or len(buffer) < byte_length:
        return num.to_bytes(byte_length, byteorder='little', signed=False)
    else:
        ctypes.memset(buffer, 0, len(buffer))
        num_bytes = num.to_bytes(byte_length, byteorder='little', signed=False)
        ctypes.memmove(buffer, num_bytes, byte_length)
        return bytes(buffer)


def int_to_bytes_highly_optimized(num: int, buffer=None):
    if num == 0:
        return b'\x00'

        # Calculate the number of bytes needed to represent the integer
    byte_length = (num.bit_length() + 7) // 8

    # If no buffer is provided or it's too small, return the bytes directly
    if buffer is None or len(buffer) < byte_length:
        return num.to_bytes(byte_length, ENDIAN_TYPE)

    # Convert integer to bytes directly into the provided buffer
    num_bytes = num.to_bytes(byte_length, ENDIAN_TYPE)

    buffer[:byte_length] = num_bytes
    return bytes(buffer[:byte_length])


# Example integer to test with
test_num = 123456789123456789123456789123456789123456789123456789123456789123456789

# Define the number of iterations for the test
iterations = 10000000

# Performance test for the original method
original_time = timeit.timeit(lambda: int_to_bytes_original(test_num), number=iterations)

# Performance test for the optimized method
optimized_time = timeit.timeit(lambda: int_to_bytes_optimized(test_num), number=iterations)
ooptimized_time = timeit.timeit(lambda: int_to_bytes_highly_optimized(test_num), number=iterations)

# Print results
print(f"Original method time: {original_time:.6f} seconds for {iterations} iterations")
print(f"Optimized method time: {optimized_time:.6f} seconds for {iterations} iterations")
print(f"Highly Optimized method time: {ooptimized_time:.6f} seconds for {iterations} iterations")
print(f"Performance improvement: {((original_time - optimized_time) / original_time) * 100:.2f}%")
print(f"Performance improvement: {((original_time - ooptimized_time) / original_time) * 100:.2f}%")
