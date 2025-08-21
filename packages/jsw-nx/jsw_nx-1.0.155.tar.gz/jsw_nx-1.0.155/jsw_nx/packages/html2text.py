from bs4 import BeautifulSoup


def html2text(html):
    """
    Convert HTML to Markdown.
    """
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    return text
