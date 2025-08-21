import os


def env_select(in_env=None):
    is_local = os.environ.get('SERVER_IP') == '127.0.0.1'
    if in_env:
        return in_env
    if is_local:
        return 'local'
    return 'remote'
