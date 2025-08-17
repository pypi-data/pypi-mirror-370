# encoding:utf-8
import hashlib
from maths_add.except_error import decorate

__all__ = [
    "encode"
]


@decorate()
def encode(text):
    data = text.encode()
    hash_object = hashlib.sha256(data)
    hash_hex = hash_object.hexdigest()
    return hash_hex
