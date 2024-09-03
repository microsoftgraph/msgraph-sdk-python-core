from typing import List, Optional, Dict, Callable

from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import Parsable
from kiota_abstractions.serialization import SerializationWriter

from .batch_request_item import BatchRequestItem


class BatchRequestContent(Parsable):
    """
    Provides operations to call the batch method.
    """

    MAX_REQUESTS = 20
    requests: List = []

    def __init__(self, requests: Optional[List] = None) -> None:
        """
        Initializes a new instance of the BatchRequestContent class.
        """
        pass

    @property
    def requests(self) -> List:
        """
        Gets and sets the requests.
        """
        pass

    def add_request(self, request: RequestInformation):
        """
        Adds a request to the batch request content.
        """
        pass

    def add_request_information(self, selfrequest_information: RequestInformation):
        pass

    def remove(seld, request_id: str):
        """
        Removes a request from the batch request content.
        """
        pass

    def remove_batch_request_item(self, item: BatchRequestItem):
        pass

    def get_field_deserializers(self, ) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        pass

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        pass
