import uuid
from typing import List, Dict, Union

from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import Parsable
from kiota_abstractions.serialization import SerializationWriter

from .batch_request_item import BatchRequestItem


class BatchRequestContent(Parsable):
    """
    Provides operations to call the batch method.
    """

    MAX_REQUESTS = 20

    def __init__(self, requests: List[Union['BatchRequestItem', 'RequestInformation']] = []):
        """
        Initializes a new instance of the BatchRequestContent class.
        """
        self._requests: List[Union[BatchRequestItem, 'RequestInformation']] = requests or []
        self.is_finalized = False

    @property
    def requests(self) -> List:
        """
        Gets  the requests.
        """
        return self._requests

    @requests.setter
    def requests(self, requests: List[BatchRequestItem]) -> None:
        if len(requests) >= BatchRequestContent.MAX_REQUESTS:
            raise ValueError(f"Maximum number of requests is {BatchRequestContent.MAX_REQUESTS}")
        for request in requests:
            self.add_request(request)

    def add_request(self, request: BatchRequestItem) -> None:
        """
        Adds a request to the batch request content.
        """
        if len(self.requests) >= BatchRequestContent.MAX_REQUESTS:
            raise RuntimeError(f"Maximum number of requests is {BatchRequestContent.MAX_REQUESTS}")
        if not request.id:
            request.id = str(uuid.uuid4())
        self._requests.append(request)

    def add_request_information(self, request_information: RequestInformation) -> None:
        self.add_request(BatchRequestItem(request_information))

    def add_urllib_request(self, request) -> None:
        self.add_request(BatchRequestItem.create_with_urllib_request(request))

    def remove(self, request_id: str) -> None:
        """
        Removes a request from the batch request content.
        """
        if request_id in self.requests:
            del self.requests[request_id]

    def remove_batch_request_item(self, item: BatchRequestItem) -> None:
        self.remove(item.id)

    def finalize(self):
        self.is_finalized = True
        return self._requests

    def get_field_deserializers(self, ) -> Dict:
        """
        The deserialization information for the current model
        """
        return {}

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        Args:
            writer: Serialization writer to use to serialize this model
        """
        writer.write_collection_of_object_values("requests", self.requests)
