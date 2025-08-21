# https://console.leancloud.cn/apps/8alQIE7rUNqk6Y7DqxPgrJvK-gzGzoHsz/storage/data/options
import requests
import os

BASE_URL = 'https://8alqie7r.lc-cn-n1-shared.com/1.1/classes/options'


class LcOption:
    def __init__(self, **kwargs):
        self.headers = {'X-LC-Id': kwargs.get('app_id', os.getenv('LEANCLOUD_ID')),
                        'X-LC-Key': kwargs.get('app_key', os.getenv('LEANCLOUD_KEY')),
                        'Content-Type': 'application/json'}

    def get(self, in_id, **kwargs):
        url = f'{BASE_URL}/{in_id}'
        res = requests.get(url, headers=self.headers, **kwargs)
        return self.process_response(res)

    def set(self, in_id, **kwargs):
        return self.put(in_id, **kwargs)

    def get_value(self, in_id, **kwargs):
        res = self.get(in_id, **kwargs)
        return res['value']

    def set_value(self, in_id, value, **kwargs):
        return self.put(in_id, data={'value': value}, **kwargs)

    def put(self, in_id, **kwargs):
        url = f'{BASE_URL}/{in_id}'
        data = kwargs.pop('data', {})
        res = requests.put(url, json=data, headers=self.headers)
        return self.process_response(res)

    @classmethod
    def process_response(cls, res):
        if res.status_code == 200:
            return res.json()
        return None
