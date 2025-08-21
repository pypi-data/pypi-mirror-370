import requests
import urllib
import hashlib

API_URL = 'https://pan.baidu.com/api'


class BaiduPanUpload:
    def __init__(self, token):
        self.headers = {"Cookie": token, }

    def upload(self, **kwargs):
        source = kwargs.get('source')
        target = kwargs.get('target')
        res1 = self.precreate()
        uploadid = res1['uploadid']
        res2 = self.superfile2(uploadid, source)
        res3 = self.create(uploadid, source, target)
        return res3.json()

    def precreate(self):
        url = API_URL + '/precreate'
        res = requests.post(
            url,
            headers=self.headers,
            data={'path': '/db.file', 'autoinit': 1, 'block_list': '[""]'}
        )
        return res.json()

    def superfile2(self, uploadid, filename):
        base_url = 'https://c3.pcs.baidu.com/rest/2.0/pcs/superfile2'
        params = {
            'method': 'upload',
            'app_id': '250528',
            'path': '/',
            'uploadid': uploadid,
            'uploadsign': 0,
            'partseq': 0
        }
        url = base_url + '?' + urllib.parse.urlencode(params)
        filep = open(filename, 'rb')

        # update headers
        return requests.post(
            url,
            headers=self.headers,
            files={'file': filep, },
        )

    def create(self, uploadid, filename, remote_path):
        # get md5 from filep
        filep = open(filename, 'rb')
        md5 = hashlib.md5(filep.read()).hexdigest()
        filesize = filep.tell()
        url = API_URL + '/create'

        return requests.post(
            url,
            headers=self.headers,
            data={
                'path': remote_path,
                'size': filesize,
                'uploadid': uploadid,
                'block_list': '["' + md5 + '"]'
            }
        )
