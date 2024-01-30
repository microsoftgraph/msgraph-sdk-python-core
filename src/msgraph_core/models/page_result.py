from kiota_abstractions.serialization.parsable import Parsable
from kiota_abstractions.serialization.serialization_writer import SerializationWriter
from kiota_abstractions.serialization.parse_node import ParseNode
from typing import Any, List, Optional


class PageResult(Parsable):

    def __init__(self):
        self._odata_next_link: Optional[str] = None
        self._value: Optional[List[Any]] = None
