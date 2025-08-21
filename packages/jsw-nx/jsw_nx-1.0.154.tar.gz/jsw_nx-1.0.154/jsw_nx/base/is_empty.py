
def is_empty(target):
    if target == None:
        return True
    elif target == "":
        return True
    elif target == []:
        return True
    elif target == {}:
        return True
    else:
        return False
