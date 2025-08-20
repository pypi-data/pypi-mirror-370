from decentnet.consensus.byte_conversion_constants import ENDIAN_TYPE


def int_to_bytes(num: int):
    if num == 0:
        return b'\x00'

    # Calculate the number of bytes needed to represent the integer
    byte_length = (num.bit_length() + 7) // 8
    return num.to_bytes(byte_length, ENDIAN_TYPE)
