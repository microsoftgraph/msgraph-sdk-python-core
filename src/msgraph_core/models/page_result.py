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
