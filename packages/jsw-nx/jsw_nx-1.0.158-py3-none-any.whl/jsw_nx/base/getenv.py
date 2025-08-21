import os


def getenv(key=None):
    if not key:
        return dict(os.environ)
    return os.environ[key]
