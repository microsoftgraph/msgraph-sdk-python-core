from typing import List, Optional, Dict, Callable

from kiota_abstractions.serialization import Parsable
from kiota_abstractions.serialization import ParseNode
from kiota_abstractions.serialization import ParseNodeFactory
from kiota_abstractions.serialization import ParseNodeFactoryRegistry
from kiota_abstractions.serialization import SerializationWriter

from .batch_response_item import BatchResponseItem


class BatchResponseContent(Parsable):
    responses = []

    def __init__(self) -> None:
        pass

    @property
    def responses(self) -> List[Parsable]:
        pass

    @property
    def response(self, request_id: str) -> BatchResponseItem:
        pass

    @property
    def response_body(self, request_id: str) -> Optional[Parsable]:
        pass

    def get_field_deserializers(self, ) -> Dict[str, Callable[[ParseNode], None]]:
        pass

    def serialize(self, writer: SerializationWriter) -> None:
        pass
