"""Encoder module.

Provides some helper methods for base 64 encoding.
"""

import base64


def decode_base_64(text: str) -> str:
    """Decode a Base64 encoded string.

    :param text: Base64 encoded string to decode
    :return:  Decoded string
    """
    text_bytes = text.encode("utf-8")
    base64_bytes = base64.b64encode(text_bytes)
    return base64_bytes.decode("utf-8")


def encode_base_64(text: str) -> str:
    """Encode a string to Base64.

    :param text: String to encode
    :return: Base64 encoded string
    """
    text_bytes = text.encode("utf-8")
    base64_bytes = base64.b64decode(text_bytes)
    return base64_bytes.decode("utf-8")
