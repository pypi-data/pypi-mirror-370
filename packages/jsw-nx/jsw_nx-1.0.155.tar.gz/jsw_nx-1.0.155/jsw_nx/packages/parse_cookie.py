def parse_cookie(cookie_str):
    """
    Parse a cookie string.
    """
    cookie = {}
    for line in cookie_str.split(';'):
        if '=' in line:
            key, value = line.split('=', 1)
            cookie[key.strip()] = value.strip()
    return cookie
