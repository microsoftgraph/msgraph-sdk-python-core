from kiota_abstractions.serialization.parsable import Parsable
from kiota_abstractions.serialization.serialization_writer import SerializationWriter
from kiota_abstractions.serialization.parse_node import ParseNode
from typing import Any, List, Optional


class PageResult(Parsable):

    def __init__(self):
        self._odata_next_link: Optional[str] = None
        self._value: Optional[List[Any]] = None

    @property
    def odata_next_link(self) -> Optional[str]:
        return self._odata_next_link

    @property
    def value(self) -> Optional[List[Any]]:
        return self._value

    @odata_next_link.setter
    def odata_next_link(self, next_link: Optional[str]) -> None:
        self._odata_next_link = next_link

    @value.setter
    def value(self, value: Optional[List[Any]]) -> None:
        self._value = value

    def create_from_discriminator_value(self, parse_node: ParseNode) -> 'PageResult':
        return PageResult()

    def set_value(self, value: List[Any]):
        self.value = value

    def get_field_deserializers(self) -> dict:
        return {
            '@odata.nextLink':
            lambda parse_node: self.odata_next_link(parse_node.get_string_value()),
            'value': self.set_value
        }

    def serialize(self, writer: 'SerializationWriter') -> None:
        writer.write_string_value('@odata.nextLink', self.odata_next_link)
        writer.write_any_value('value', self.value)
