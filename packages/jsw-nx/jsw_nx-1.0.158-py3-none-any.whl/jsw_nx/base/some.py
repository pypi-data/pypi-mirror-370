def some(arr, fn):
    res = False
    for i, v in enumerate(arr):
        res = res or fn(v, i)
    return res
