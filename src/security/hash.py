import hashlib


def hash_key(key_value: str) -> str:
    return hashlib.sha256(key_value.encode()).hexdigest()
