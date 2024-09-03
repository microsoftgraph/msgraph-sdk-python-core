from typing import List, Optional, Dict, Callable

from kiota_abstractions.serialization import Parsable
from kiota_abstractions.serialization import ParseNode
from kiota_abstractions.serialization import ParseNodeFactory
from kiota_abstractions.serialization import ParseNodeFactoryRegistry
from kiota_abstractions.serialization import SerializationWriter

from .batch_response_content import BatchResponseContent


class BatchResponseContentCollection(Parsable):

    def __init__(self) -> None:
        pass

    def get_response(self, request_id: str) -> BatchResponseContent:
        pass

    def get_response_status_codes():
        pass
