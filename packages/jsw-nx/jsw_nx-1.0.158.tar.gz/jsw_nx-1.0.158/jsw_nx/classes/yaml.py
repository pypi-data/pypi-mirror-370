from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

yaml = YAML()


# https://blog.csdn.net/BreezePython/article/details/108770195
# https://www.cnblogs.com/jiahm/p/13828140.html
# https://yaml.readthedocs.io/en/latest/example.html

class Yaml:
    @classmethod
    def stringify(cls, data):
        stream = StringIO()
        yaml.dump(data, stream)
        return stream.getvalue()

    @classmethod
    def parse(cls, data):
        return yaml.load(data)
