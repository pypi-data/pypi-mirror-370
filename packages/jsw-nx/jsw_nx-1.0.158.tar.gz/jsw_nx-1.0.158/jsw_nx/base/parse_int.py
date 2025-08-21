def parse_int(s1):
    try:
        variable = int(s1)
    except ValueError:
        variable = None
    return variable
