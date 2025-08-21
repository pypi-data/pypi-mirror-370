import logging
import json
import xmltodict
from abc import ABC, abstractmethod
from lasutils.helpers import get_nested

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Abstract class to serialize from dict to <format x>.
class Serializer(ABC):
    def __call__(self, data):
        return self.serialize(data)

    @abstractmethod
    def serialize(self, data: dict):
        pass


# JSON
class JsonSerializer(Serializer):
    def __init__(self):
        super().__init__()

    def serialize(self, data: dict):
        if not data:
            return None
        return json.dumps(data)


# XML
class XmlSerializer(Serializer):
    def __init__(self):
        super().__init__()

    def serialize(self, data: dict, top_node_name="root"):
        if not data:
            return None
        # XML needs a single top node
        if len(data) != 1:
            data = {top_node_name: data}
        return xmltodict.unparse(data)


# NOP
class NoSerializer(Serializer):
    def __init__(self):
        super().__init__()

    def serialize(self, data: dict):
        if not data:
            return None
        return data


# Factory method for deserializers
def create_serializer(serializer_name: str = "nop") -> Serializer:
    serializers = {
        "json": JsonSerializer,
        "xml": XmlSerializer,
        "nop": NoSerializer,
        "raw": NoSerializer,
    }
    serializer_class = serializers.get(serializer_name.lower())
    if not serializer_class:
        logger.error(f'Serializer "{serializer_name}" not found')
    return serializer_class()
