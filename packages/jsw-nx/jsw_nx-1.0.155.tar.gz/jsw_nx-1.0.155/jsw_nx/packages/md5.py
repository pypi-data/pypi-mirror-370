import hashlib


def md5(string, encoding='utf-8'):
    return hashlib.md5(string.encode(encoding)).hexdigest()
