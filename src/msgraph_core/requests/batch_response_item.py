from typing import List, Optional, Dict, Callable

from kiota_abstractions.serialization import Parsable
from kiota_abstractions.serialization import ParseNode
from kiota_abstractions.serialization import SerializationWriter


class BatchResponseItem(Parsable):

    id: str = None
    status_code: int = None
    headers: Dict[str, str] = None
    atomicity_group: str = None

    def __init__(self) -> None:
        """
        Initializes a new instance of the BatchResponseItem class.
        """
        pass

    def get_field_deserializers(self, ) -> Dict[str, Callable[[ParseNode], None]]:
        pass

    def serialize(self, writer: SerializationWriter) -> None:
        pass
