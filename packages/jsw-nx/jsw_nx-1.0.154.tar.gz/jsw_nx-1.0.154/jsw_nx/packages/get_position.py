# https://tva1.sinaimg.cn/large/008vxvgGgy1h7u1m6nmvkj30gh0evt92.jpg
def get_position(position, large, small, offset):
    if position == 'center':
        x = large[0] // 2 - small[0] // 2
        y = large[1] // 2 - small[1] // 2
    elif position == 'south':
        x = large[0] // 2 - small[0] // 2
        y = large[1] - small[1] - offset[1]
    elif position == 'north':
        x = large[0] // 2 - small[0] // 2
        y = offset[1]
    elif position == 'west':
        x = offset[0]
        y = large[1] // 2 - small[1] // 2
    elif position == 'east':
        x = large[0] - small[0] - offset[0]
        y = large[1] // 2 - small[1] // 2
    elif position == 'southeast':
        x = large[0] - small[0] - offset[0]
        y = large[1] - small[1] - offset[1]
    elif position == 'southwest':
        x = offset[0]
        y = large[1] - small[1] - offset[1]
    elif position == 'northwest':
        x = offset[0]
        y = offset[1]
    elif position == 'northeast':
        x = large[0] - small[0] - offset[0]
        y = offset[1]
    else:
        x = large[0] - small[0] - offset[0]
        y = large[1] - small[1] - offset[1]
    return x, y
