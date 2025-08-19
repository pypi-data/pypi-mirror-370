import logging
import json
import xmltodict
from abc import ABC, abstractmethod
from lasutils.helpers import get_nested

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DATA_PATH_SEP = "."

# Abstract class to deserialize from <format x> to dict.
class Deserializer(ABC):
    def __call__(self, data: str, data_path: str = None):
        return self.deserialize(data, data_path)

    @abstractmethod
    def deserialize(self, data: str = "", data_path: str = None):
        pass

    def get_subtree(self, data: dict = {}, tree_path: str = None):
        if not tree_path:
            return data

        tree_path = tree_path.split(DATA_PATH_SEP)
        try:
            return get_nested(data, tree_path)
        except KeyError as key:
            logger.error(
                f'Key "{key}" in path "{tree_path}" was not found in data:\n {data}'
            )
            return


# JSON
class JsonDeserializer(Deserializer):
    def __init__(self):
        super().__init__()

    def deserialize(self, data: str, data_path: str = None):
        if not data:
            return None
        jd = json.loads(data)
        return self.get_subtree(jd, data_path)


# XML
class XmlDeserializer(Deserializer):
    def __init__(self):
        super().__init__()

    def deserialize(self, data: str, data_path: str = None):
        if not data:
            return None
        xmld = xmltodict.parse(data, dict_constructor=dict, xml_attribs=False)
        return self.get_subtree(xmld, data_path)


# NOP
class NoDeserializer(Deserializer):
    def __init__(self):
        super().__init__()

    def deserialize(self, data: str, data_path: str = None):
        return data


# Factory method for deserializers
def create_deserializer(deserializer_name: str = "nop") -> Deserializer:
    deserializers = {
        "json": JsonDeserializer,
        "xml": XmlDeserializer,
        "nop": NoDeserializer,
        "raw": NoDeserializer,
    }
    deserializer_class = deserializers.get(deserializer_name.lower())
    if not deserializer_class:
        logger.error(f'Deserializer "{deserializer_name}" not found')
    return deserializer_class()
