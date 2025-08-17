# encoding:utf-8
from maths_add.except_error import decorate
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

__all__ = [
    "getKey",
    "getIv",
    "encode",
    "decode",
    "saveKey",
    "saveIv",
    "saveEncodeFile",
    "saveDecodeFile"
]


def getKey():
    return get_random_bytes(16)


def getIv():
    return get_random_bytes(16)


@decorate()
def encode(plaintext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    return ciphertext


@decorate()
def decode(ciphertext, key, iv):
    decipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_padded_text = decipher.decrypt(ciphertext)
    decrypted_text = unpad(decrypted_padded_text, AES.block_size)
    return decrypted_text


@decorate()
def saveKey(FilePath, key):
    with open(FilePath, "wb") as f:
        f.write(key)


@decorate()
def saveIv(FilePath, iv):
    with open(FilePath, "wb") as f:
        f.write(iv)


@decorate()
def saveEncodeFile(FilePath, plaintext):
    with open(FilePath, "wb") as f:
        f.write(plaintext)


@decorate()
def saveDecodeFile(FilePath, ciphertext):
    with open(FilePath, "wb") as f:
        f.write(ciphertext)


if __name__ == '__main__':
    pass
