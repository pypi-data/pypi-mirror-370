import random


def sample(arr, count=None):
    if not count:
        res = random.sample(arr, 1)
        return res[0]
    return random.sample(arr, count)
