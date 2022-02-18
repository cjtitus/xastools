from .yamlExport import loadFromYaml
from .ssrlExport import loadFromSSRL
from tiled.adapters.array import ArrayAdapter


class SSRLAdapter(ArrayAdapter):
    specs = ['nistxas']

    @classmethod
    def from_file(cls, filepath):
        data, header = loadFromSSRL(filepath)
        return cls.from_array(data, metadata=header)


class YamlAdapter(ArrayAdapter):
    specs = ['nistxas']

    @classmethod
    def from_file(cls, filepath):
        data, header = loadFromYaml(filepath)
        return cls.from_array(data, metadata=header)
