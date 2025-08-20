import base64
from builtins import memoryview


def bytes_to_base64(data: bytes | memoryview) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8")


def base64_to_original(data: str) -> bytes | str:
    return base64.urlsafe_b64decode(data)


def base85_to_original(data: str) -> bytes | str:
    return base64.b85decode(data)


def bytes_to_base85(data: bytes) -> str:
    return base64.b85encode(data).decode("utf-8")
