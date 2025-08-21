import requests
import string
import random

"""
原理: 
1. 自己指定密码，可以是固定，可以是随机密码
2. 调用 share 相关的接口/post 对应的数据，即可完成分享
3. 返回我这边只取 url/password 返回
"""


class BaiduPanShare:
    def __init__(self, token):
        self.headers = {"Cookie": token, }

    def share(self, **kwargs):
        password = kwargs.get('password', self.generate_password(4))
        fid = kwargs.get('fid')

        url = 'https://pan.baidu.com/share/set'
        res = requests.post(
            url,
            headers=self.headers,
            data={
                'period': 0,
                'pwd': password,
                'eflag_disable': 'true',
                'schannel': 4,
                'channel_list': '[]',
                'fid_list': '[%s]' % fid,
            }
        ).json()

        return {'url': res['link'], 'password': password, }

    @classmethod
    def generate_password(cls, size):
        res = ''.join(random.choices(string.ascii_lowercase +
                                     string.digits, k=size))
        return str(res)
