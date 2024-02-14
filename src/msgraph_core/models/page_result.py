from kiota_abstractions.serialization.parsable import Parsable  # type: ignore
from kiota_abstractions.serialization.parsable_factory import ParsableFactory  # type: ignore
from kiota_abstractions.serialization.serialization_writer import SerializationWriter  # type: ignore
from kiota_abstractions.serialization.parse_node import ParseNode  # type: ignore
from kiota_serialization_json.json_parse_node import JsonParseNode  # type: ignore
from kiota_serialization_json.json_parse_node_factory import JsonParseNodeFactory  # type: ignore
from typing import Any, List, Optional
import importlib


class PageResult(Parsable):
    object_type = None

    def __init__(self, object_type: Optional[Any] = None) -> None:
        PageResult.object_type = object_type
        self._odata_next_link: Optional[str] = None
        self._value: Optional[List[Any]] = None

    @property
    def odata_next_link(self) -> Optional[str]:
        return self._odata_next_link

    @odata_next_link.setter
    def odata_next_link(self, next_link: Optional[str]) -> None:
        self._odata_next_link = next_link

    @property
    def value(self) -> Optional[List[Any]]:
        return self._value

    @value.setter
    def value(self, value: Optional[List[Any]]) -> None:
        self._value = value

    @staticmethod
    def create_from_discriminator_value(node: ParseNode) -> 'PageResult':
        impprt_statement = f"from msgraph.generated.models.message import {PageResult.object_type}"
        exec(impprt_statement)
        if isinstance(PageResult.object_type, str):
            return PageResult(locals()[PageResult.object_type])
        return PageResult()

    def set_value(self, value: List[Any]):
        self.value = value

    def get_field_deserializers(self):
        class_name = PageResult.object_type

        instance = class_name()
        module_path = instance.__class__.__module__
        class_name = instance.__class__.__name__
        import_statement = f'from {module_path} import {class_name}'
        exec(import_statement)
        serialization_model = locals()[class_name]
        return {
            '@odata.nextLink':
            lambda parse_node: setattr(self, 'odata_next_link', parse_node.get_str_value()),
            'value':
            lambda parse_node: self.
            set_value(parse_node.get_collection_of_object_values(serialization_model))
        }

    def serialize(self, writer: SerializationWriter) -> None:
        writer.write_str_value('@odata.nextLink', self.odata_next_link, self.value)
        if self.value is not None:
            writer.write_collection_of_object_values('key', 'value', list(self.value))
