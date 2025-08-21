import requests
import os
import json
import jsw_nx as nx

BASE_URL = 'https://api.day.app'
ARIC_ICON = 'https://tva1.sinaimg.cn/large/007S8ZIlgy1gexw87htqhj305k05k74o.jpg'


def notify(**kwargs):
    bark_key = kwargs.get('bark_key') or os.environ["BARK_SDK_KEY"]
    kwargs.setdefault('icon', ARIC_ICON)
    kwargs.setdefault('title', 'Tips')
    api_url = f'{BASE_URL}/{bark_key}'
    return requests.post(api_url, json=kwargs)
