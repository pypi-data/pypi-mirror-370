import random
import os
import hashlib
import requests

DEFAULTS = {
    "q": "apple",
    "salt": str(random.random()),
    "appid": os.getenv("BAIDU_FANYI_APP_ID"),
    "secret": os.getenv("BAIDU_FANYI_APP_SECRET"),
}


class Fanyi:
    def __init__(self, **kwargs):
        self.options = DEFAULTS
        self.options.update(kwargs)
        self.url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'

    def sign(self):
        options = self.options.copy()

        # 提取出变量
        q = options["q"]
        salt = options["salt"]
        secret = options["secret"]
        appid = options["appid"]

        # 计算签名并添加到选项中
        res = appid + q + salt + secret
        m = hashlib.md5()
        m.update(res.encode())
        sign = m.hexdigest()
        options["sign"] = sign

        return options

    def translate(self, options):
        # 计算签名添加到选项中
        opts = self.sign()
        opts.update(options)
        r = requests.get(self.url, params=opts)
        return r.json()
