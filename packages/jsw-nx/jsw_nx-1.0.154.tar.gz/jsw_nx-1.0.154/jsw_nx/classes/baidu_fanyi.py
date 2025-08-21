from .baidu.fanyi import Fanyi

DEFAULTS = {
    "from": "en",
    "to": "zh",
}


class BaiduFanyi:
    @classmethod
    def translate(cls, **kwargs):
        q = kwargs.pop("q", "apple")
        opts = DEFAULTS.copy()
        opts.update(kwargs)
        slim = kwargs.get('slim', False)
        res = Fanyi(q=q, **kwargs).translate(opts)
        if slim:
            return res["trans_result"]
        else:
            return res
