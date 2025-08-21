def forin(obj, fn):
    the_type = type(obj)
    if the_type is dict:
        for key in obj:
            fn(key, obj[key])
    if the_type is list:
        for i in range(len(obj)):
            fn(i, obj[i])
    if the_type is tuple:
        for i in range(len(obj)):
            fn(i, obj[i])