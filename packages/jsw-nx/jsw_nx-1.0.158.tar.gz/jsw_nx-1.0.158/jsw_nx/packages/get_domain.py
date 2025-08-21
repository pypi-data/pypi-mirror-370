from urllib.parse import urlparse


def get_domain(url):
    """
    Get the domain name from a URL.
    """
    return urlparse(url).netloc
