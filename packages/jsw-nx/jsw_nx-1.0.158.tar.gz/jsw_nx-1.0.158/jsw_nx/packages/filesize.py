import os


# https://www.alpharithms.com/python-get-file-size-271811/

def filesize(filename):
    size = os.stat(filename).st_size

    # Convert to familiar units
    kb = size / 1024
    mb = size / 1024 / 1024

    kb_2 = str(round(kb, 2)) + 'KB'
    mb_2 = str(round(mb, 2)) + 'MB'

    return size, kb_2, mb_2
