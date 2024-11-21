import uuid
from typing import List, Dict, Union, Optional

from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import Parsable, ParseNode
from kiota_abstractions.serialization import SerializationWriter

from .batch_request_item import BatchRequestItem


class BatchRequestContent(Parsable):
    """
    Provides operations to call the batch method.
    """

    MAX_REQUESTS = 20

    def __init__(self, requests: Dict[str, Union['BatchRequestItem', 'RequestInformation']] = {}):
        """
        Initializes a new instance of the BatchRequestContent class.
        """
        self._requests: Dict[str, Union[BatchRequestItem, 'RequestInformation']] = requests or {}

        self.is_finalized = False
        for request_id, request in requests.items():
            self.add_request(request_id, request)

    @property
    def requests(self) -> Dict:
        """
        Gets  the requests.
        """
        return self._requests

    @requests.setter
    def requests(self, requests: List[BatchRequestItem]) -> None:
        """
        Sets the requests.
        """
        if len(requests) >= BatchRequestContent.MAX_REQUESTS:
            raise ValueError(f"Maximum number of requests is {BatchRequestContent.MAX_REQUESTS}")
        for request in requests:
            self.add_request(request.id, request)

    def add_request(self, request_id: Optional[str], request: BatchRequestItem) -> None:
        """
        Adds a request to the batch request content.
        """
        if len(self.requests) >= BatchRequestContent.MAX_REQUESTS:
            raise RuntimeError(f"Maximum number of requests is {BatchRequestContent.MAX_REQUESTS}")
        if not request.id:
            request.id = str(uuid.uuid4())
        if hasattr(request, 'depends_on') and request.depends_on:
            for dependent_id in request.depends_on:
                if dependent_id not in self.requests:
                    dependent_request = self._request_by_id(dependent_id)
                    if dependent_request:
                        self._requests[dependent_id] = dependent_request
        self._requests[request.id] = request

    def add_request_information(self, request_information: RequestInformation) -> None:
        """ 
        Adds a request to the batch request content.
        Args:
            request_information (RequestInformation): The request information to add.
        """
        request_id = str(uuid.uuid4())
        self.add_request(request_id, BatchRequestItem(request_information))

    def add_urllib_request(self, request) -> None:
        """
        Adds a request to the batch request content.
        """
        request_id = str(uuid.uuid4())
        self.add_request(request_id, BatchRequestItem.create_with_urllib_request(request))

    def remove(self, request_id: str) -> None:
        """
        Removes a request from the batch request content.
        Also removes the request from the depends_on list of 
            other requests.
        """
        request_to_remove = None
        for request in self.requests:
            if request.id == request_id:
                request_to_remove = request
            if hasattr(request, 'depends_on') and request.depends_on:
                if request_id in request.depends_on:
                    request.depends_on.remove(request_id)
        if request_to_remove:
            del self._requests[request_to_remove.id]
        else:
            raise ValueError(f"Request ID {request_id} not found in requests.")

    def remove_batch_request_item(self, item: BatchRequestItem) -> None:
        """
        Removes a request from the batch request content.
        """
        self.remove(item.id)

    def finalize(self):
        """
        Finalizes the batch request content.
        """
        self.is_finalized = True
        return self._requests

    def _request_by_id(self, request_id: str) -> Optional[BatchRequestItem]:
        """
        Finds a request by its ID.
        
        Args:
            request_id (str): The ID of the request to find.

        Returns:
            The request with the given ID, or None if not found.
        """
        return self._requests.get(request_id)

    @staticmethod
    def create_from_discriminator_value(
        parse_node: Optional[ParseNode] = None
    ) -> 'BatchRequestContent':
        if parse_node is None:
            raise ValueError("parse_node cannot be None")
        return BatchRequestContent()

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
