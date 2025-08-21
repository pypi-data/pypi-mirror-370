import json


class JsonUtils(object):
    @classmethod
    def parse(cls, json_str):
        return json.loads(json_str)

    @classmethod
    def stringify(cls, obj, **kwargs):
        return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True, **kwargs)
