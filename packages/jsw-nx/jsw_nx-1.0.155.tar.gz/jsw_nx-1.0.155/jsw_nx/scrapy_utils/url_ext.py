import os
from urllib.parse import urlparse


def url_ext(url):
    """
    Extract the extension of a URL.
    """
    urlpath = urlparse(url).path
    ext = os.path.splitext(urlpath)[1]
    return ext[1:]
