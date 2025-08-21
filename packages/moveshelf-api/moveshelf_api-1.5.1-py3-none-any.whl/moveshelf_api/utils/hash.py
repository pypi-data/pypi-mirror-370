"""
Hash utility functions for file integrity verification.

This module provides functions for calculating various hash checksums
of files and data streams, optimized for handling large files common
in motion capture workflows.
"""

import base64
import hashlib
import struct

import six
from crcmod.predefined import mkPredefinedCrcFun

crc32c_func = mkPredefinedCrcFun('crc32c')

def calculate_file_md5(file_path: str) -> str:
    """
    Calculate MD5 hash of a local file using chunk reading.

    Uses chunk reading to avoid loading large files entirely into memory,
    which is crucial for motion capture files that can be several GB in size.

    Args:
        file_path: Path to the file to calculate MD5 for.

    Returns:
        Hexadecimal string representation of the MD5 hash.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def calculate_stream_md5(response) -> str:
    """
    Calculate MD5 hash of a streaming HTTP response using chunk reading.

    Uses chunk reading to avoid loading large downloaded files entirely into memory,
    which is crucial for motion capture files that can be several GB in size.

    Args:
        response: urllib3 HTTPResponse object with preload_content=False.

    Returns:
        Hexadecimal string representation of the MD5 hash.
    """
    hash_md5 = hashlib.md5()
    for chunk in response.stream(4096):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()


def calculate_file_crc32c(file_path: str) -> str:
    """
    Calculate the CRC32C checksum of a file.

    Args:
        file_path: The path to the file to calculate the checksum for.

    Returns:
        The Base64-encoded CRC32C checksum.
    """
    with open(file_path, 'rb') as fp:
        crc = crc32c_func(fp.read())
        b64_crc = base64.b64encode(struct.pack('>I', crc))
        return b64_crc if six.PY2 else b64_crc.decode('utf8')
