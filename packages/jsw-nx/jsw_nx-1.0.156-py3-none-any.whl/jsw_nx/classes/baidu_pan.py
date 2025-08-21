from .lc_option import LcOption
from .baidu.pan_upload import BaiduPanUpload
from .baidu.pan_share import BaiduPanShare

API_URL = 'https://pan.baidu.com/api'
BAIDU_PAN_TOKEN_ID = '636484ab9c1aea6e1d70952d'


class BaiduPan:
    @property
    def headers(self):
        return {"Cookie": self.token, }

    def __init__(self, token=None):
        self.token = token or LcOption().get_value(BAIDU_PAN_TOKEN_ID)
        self.uploader = BaiduPanUpload(self.token)
        self.sharer = BaiduPanShare(self.token)

    ## 上传文件
    def upload(self, **kwargs):
        return self.uploader.upload(**kwargs)

    def share(self, **kwargs):
        return self.sharer.share(**kwargs)
