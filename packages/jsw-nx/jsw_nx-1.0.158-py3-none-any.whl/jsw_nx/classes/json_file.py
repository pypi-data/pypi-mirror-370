import json
import os


class JsonFile:
    @classmethod
    def parse(cls, json_str):
        return json.loads(json_str)

    @classmethod
    def stringify(cls, obj, **kwargs):
        return json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True, **kwargs)

    def __init__(self, **kwargs):
        self.path = kwargs.get('path')
        self.indent = kwargs.get('indent', 2)
        self.charset = kwargs.get('charset', 'utf-8')
        self.data = {}
        self.extra_fields = kwargs.get('extra_fields')  # function, optional

        # ensure parent path exist
        if self.path:
            parent = os.path.dirname(self.path)
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)
            if not os.path.exists(self.path):
                with open(self.path, 'w', encoding=self.charset) as f:
                    json.dump({}, f, indent=self.indent, ensure_ascii=False)
            self.read()

    def read(self):
        if not self.path or not os.path.exists(self.path):
            self.data = {}
            return self.data
        try:
            with open(self.path, 'r', encoding=self.charset) as f:
                content = f.read().strip()
                if not content:
                    self.data = {}
                else:
                    self.data = json.loads(content)
        except Exception:
            self.data = {}
        return self.data

    def write(self):
        if not self.path:
            raise ValueError("No file path specified.")
        with open(self.path, 'w', encoding=self.charset) as f:
            json.dump(self.data, f, indent=self.indent, ensure_ascii=False)

    def set(self, key, value):
        keys = key.split('.')
        d = self.data
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    def get(self, key, default=None):
        keys = key.split('.')
        d = self.data
        for k in keys:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return default
        return d

    def update(self, json_obj):
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and isinstance(d.get(k), dict):
                    deep_update(d[k], v)
                else:
                    d[k] = v

        deep_update(self.data, json_obj)
        self.save()

    def save(self, json_obj):
        self.data = json_obj
        # 自动扩展字段
        if self.extra_fields and callable(self.extra_fields):
            extra = self.extra_fields()
            if isinstance(extra, dict):
                self.data.update(extra)
        self.write()
