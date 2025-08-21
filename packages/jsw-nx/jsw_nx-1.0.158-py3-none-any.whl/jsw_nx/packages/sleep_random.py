import time
import random


def sleep_random(**kwargs):
    start = kwargs.get('start', 0.1)
    end = kwargs.get('end', 5.5)
    rand_sec = random.uniform(start, end)
    time.sleep(rand_sec)
