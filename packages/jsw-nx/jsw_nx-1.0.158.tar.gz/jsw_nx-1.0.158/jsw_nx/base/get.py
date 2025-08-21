# https://gist.github.com/wonderbeyond/085f7a8a4bfbf092b830
# https://pypi.org/project/dict-deep/

def __normalize(path):
    return path.replace('[', '.').replace(']', '').replace('..', '.')


def __is_num_like(value):
    return isinstance(value, int) or value.isdigit()


def __can_get(target):
    return isinstance(target, dict) or isinstance(target, list)


def __get(obj, key):
    if not __can_get(obj):
        return None
    if __is_num_like(key):
        return obj[int(key)]
    else:
        return obj.get(key)


def get(data, key=None, default=None, raising=False):
    if not key:
        return data
    indexes_path = __normalize(key)
    paths = indexes_path.split('.')
    result = data

    for path in paths:
        result = result and __get(result, path)

    if raising and result is None:
        raise KeyError(f"KeyError: {key}")

    return default if result is None else result
