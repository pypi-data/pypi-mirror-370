import random
import string


def random_str(length):
    letters = string.ascii_lowercase + string.digits
    result = ''.join(random.choice(letters) for i in range(length))
    return result


def random_int(length):
    return random.randint(0, 10 ** length)
