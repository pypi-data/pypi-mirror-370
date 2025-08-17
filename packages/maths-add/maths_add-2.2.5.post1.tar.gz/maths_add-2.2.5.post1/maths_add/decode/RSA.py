# encoding:utf-8
from maths_add.except_error import decorate
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import PublicFormat

__all__ = [
    "encode",
    "decode",
    "getPrivate_key",
    "getPublic_key",
    "rehabilitate",
    "savePrivate_Key",
    "savePublic_Key",
    "saveEncodeFile",
    "saveDecodeFile"
]


@decorate()
def encode(message, public_key):
    encrypted = public_key.encrypt(message,
                                   padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(),
                                                label=None))
    return encrypted


@decorate()
def decode(message, private_key):
    decrypted = private_key.decrypt(message,
                                    padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(),
                                                 label=None))
    return decrypted


@decorate()
def getPrivate_key(isConvert=True):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    if isConvert:
        key = key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8,
                                encryption_algorithm=serialization.NoEncryption())
    return key


@decorate()
def getPublic_key(private_key, isConvert=True):
    key = private_key.public_key()
    if isConvert:
        key = key.public_bytes(encoding=serialization.Encoding.PEM, format=PublicFormat.PKCS1)
    return key


@decorate()
def rehabilitate(key, key_type):
    if not isinstance(key_type, (str)):
        raise TypeError("The key_type must be a string")
    if key_type not in ["private_key", "public_key"]:
        raise ValueError("The key_type must be 'private_key' or 'public_key'")
    try:
        if key_type == 'private_key':
            key = serialization.load_pem_private_key(key, password=None, backend=default_backend())
        if key_type == 'public_key':
            key = serialization.load_pem_public_key(key, backend=default_backend())
    except Exception as e:
        print(e)
    return key


@decorate()
def savePrivate_Key(FilePath, private_key):
    with open(FilePath, "wb") as f:
        f.write(private_key)


@decorate()
def savePublic_Key(FilePath, public_key):
    with open(FilePath, "wb") as f:
        f.write(public_key)


@decorate()
def saveEncodeFile(FilePath, encrypted):
    with open(FilePath, "wb") as f:
        f.write(encrypted)


@decorate()
def saveDecodeFile(FilePath, decrypted):
    with open(FilePath, "wb") as f:
        f.write(decrypted)
