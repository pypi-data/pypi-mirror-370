import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# https://kellis-ng-alo7-com.oss-cn-beijing.aliyuncs.com/documents/f906b5df6fec876d76775a3c7aca60a8.pptx?Expires=1755925913&OSSAccessKeyId=LTAI5tSfywws519stBvtNg6R&Signature=h4IAfj6xl3yGQM4rpBp%2FeJ375aA%3D
def url_ts(url, field='ts'):
    # 解析URL
    parts = urlparse(url)
    query = parse_qs(parts.query)
    # 设置/更新ts参数
    query[field] = [str(int(time.time()))]
    # 重新编码query
    new_query = urlencode(query, doseq=True)
    # 构造新URL
    return urlunparse(parts._replace(query=new_query))
