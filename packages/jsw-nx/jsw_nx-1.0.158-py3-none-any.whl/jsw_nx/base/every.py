def every(arr, fn):
    res = True
    for i, v in enumerate(arr):
        res = res and fn(v, i)
    return res
