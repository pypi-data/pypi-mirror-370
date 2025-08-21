import requests
import json
import re
import io
from .lc_option import LcOption

# https://houbb.github.io/2019/02/25/github-09-pic-bed


TARGET_RE = r'"pics":(.*)\}\}'
PIC_HOST = 'https://tva1.sinaimg.cn/'
SIZES = 'large|bmiddle|mw1024|mw690|small|square|thumb180|thumbnail'.split('|')
API_URL = 'https://picupload.weibo.com/interface/pic_upload.php?ori=1&data={}&mime=image%2F{}'


class Weibo:

    @staticmethod
    def help():
        helpstr = """
    基本功能说明:
    1. 上传图片到 weibo，并获取地址
    2. 支持 jpg/png/gif 等常用图片格式，不过，返回地址是 jpg/gif 2种格式
    3. 只支持单张图片上传，不支持多张图片上传
    
    参考说明：
    source: 原始图片路径 或者 base64 串
    mode: 上传模式，可选值为 base64 | file(string) | url | buffer
    format: 图片格式，可选值为 jpg/gif
    debug: 是否开启 debug 模式，可选值为 True/False
            """
        print(helpstr)

    @property
    def headers(self):
        return {'Cookie': f'SUB={self.token}', 'Referer': 'https://weibo.com/'}

    def __init__(self, **kwargs):
        lc_opt = LcOption()
        res = lc_opt.get('60f768f6d9f1465d3b1d5c43')
        self.token = res['value']
        self.pic_host = kwargs.get('pic_host') or PIC_HOST

    @classmethod
    def get_format(cls, pid):
        if not pid:
            return None
        if pid[21] == 'g':
            return 'gif'
        return 'jpg'

    @classmethod
    def get_pid(cls, url):
        # https://tva1.js.work/small/da432263gy1ho5t9kynl2j20u00cqwmo.jpg
        if not url:
            return None
        id_str = url.split('/')[-1].split('.')[0]
        return int(id_str)

    # Get the image url by pid and size.
    def get(self, pid, size='large'):
        if size not in SIZES:
            size = 'large'
        return self.pic_host + size + '/' + pid + '.' + self.get_format(pid)

    # Get all kinds of image url by pid.
    def getall(self, pid):
        return {
            'large': self.get(pid, 'large'),
            'bmiddle': self.get(pid, 'bmiddle'),
            'mw1024': self.get(pid, 'mw1024'),
            'mw690': self.get(pid, 'mw690'),
            'small': self.get(pid, 'small'),
            'square': self.get(pid, 'square'),
            'thumb180': self.get(pid, 'thumb180'),
            'thumbnail': self.get(pid, 'thumbnail'),
        }

    # Upload image by url.
    def upload(self, **kwargs):
        source = kwargs.get('source')
        mode = kwargs.get('mode', 'file')
        fmt = kwargs.get('format', 'jpg')
        debug = kwargs.get('debug', False)
        files = {'pic1': source, }
        if mode == 'file':
            filep = open(source, 'rb')
            files = {'pic1': filep, }
        elif mode == 'base64':
            filep = source
            files = {'b64_data': filep}
        elif mode == 'url':
            res = requests.get(source, verify=False)
            filep = res.content
            files = {'pic1': filep}
        # 这种适合 Pillow 这种创建的图片的情况
        elif mode == 'buffer':
            filep = io.BytesIO(source.getvalue())
            files = {'pic1': filep}
        else:   
            raise ValueError('Invalid mode: {}'.format(mode))

        url = API_URL.format(mode, fmt)
        res = requests.post(url, files=files, headers=self.headers)
        html = res.text

        if debug:
            print(url, files, self.headers)
            print("Response HTML: ", html)

        target_str = re.findall(TARGET_RE, html)[0]
        json_data = json.loads(target_str)
        pdata = json_data.get('pic_1')
        pid = pdata.get('pid', None)
        response_format = self.get_format(pid)
        is_success = bool(pid) and pdata.get('width', 0) > 0

        if is_success:
            return {
                'success': True,
                'pid': pid,
                'url': self.get(pid, 'large'),
                'format': response_format,
                **pdata
            }
        else:
            return {
                'success': False,
                'pid': None,
                'url': None,
                'format': None,
                **pdata
            }
