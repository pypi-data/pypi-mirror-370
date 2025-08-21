def foreach(arr, func):
    for index, item in enumerate(arr):
        func(item, index, arr)