import hashlib
import os
import orjson

from typing import BinaryIO
from dxtrx.utils.string import normalize_string
from dxtrx.utils import json

def generate_random_sha256():
    random_bytes = os.urandom(32)  # 256-bit random
    return hashlib.sha256(random_bytes).hexdigest()

def hash_bytes_sha256(bytes: bytes) -> str:
    """
    Generate a SHA-256 hash from a bytes object.
    
    Args:
        bytes: The bytes object to hash
        
    Returns:
        str: The hexadecimal string representation of the SHA-256 hash
    """
    return hashlib.sha256(bytes).hexdigest()

def hash_string_sha256(string: str) -> str:
    """
    Generate a SHA-256 hash from a string.
    
    Args:
        string: The string to hash
        
    Returns:
        str: The hexadecimal string representation of the SHA-256 hash
    """
    return hashlib.sha256(string.encode("utf-8")).hexdigest()

def hash_object_sha256(obj: dict, normalize: bool = True) -> str:
    """
    Generate a SHA-256 hash from a dictionary object.
    The object is first converted to a JSON string before hashing.
    
    Args:
        obj: The dictionary object to hash
        normalize: Whether to normalize the string before hashing. Defaults to True due to legacy reasons.
        
    Returns:
        str: The hexadecimal string representation of the SHA-256 hash
    """
    canonical_json = json.dumps(obj, option=orjson.OPT_SORT_KEYS)
    if normalize:
        normalized_json = normalize_string(canonical_json)
        return hash_string_sha256(normalized_json)
    else:
        return hash_string_sha256(canonical_json)

def hash_file_streaming_sha256(file_like: BinaryIO) -> str:
    """
    Generate a SHA-256 hash from a file-like object using streaming.
    This is memory efficient as it reads the file in chunks rather than loading it entirely into memory.
    
    Args:
        file_like: A file-like object that supports reading in binary mode
        
    Returns:
        str: The hexadecimal string representation of the SHA-256 hash
    """
    h = hashlib.sha256()

    while True:
        # Reading is buffered, so we can read smaller chunks.
        chunk = file_like.read(h.block_size)
        if not chunk:
                break
        h.update(chunk) 

    return h.hexdigest()