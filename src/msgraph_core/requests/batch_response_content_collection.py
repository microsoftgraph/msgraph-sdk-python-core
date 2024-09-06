from typing import List, Optional, Dict, Callable

from kiota_abstractions.serialization import Parsable
from kiota_abstractions.serialization import ParseNode
from kiota_abstractions.serialization import ParseNodeFactory
from kiota_abstractions.serialization import ParseNodeFactoryRegistry
from kiota_abstractions.serialization import SerializationWriter

from .batch_response_content import BatchResponseContent
from .batch_response_item import BatchResponseItem


class BatchResponseContentCollection(Parsable):

    def __init__(self) -> None:
        """
        Initializes a new instance of the BatchResponseContentCollection class.
        BatchResponseContentCollection is a collection of BatchResponseContent items, each with
        a unique request ID.
        headers: Optional[Dict[str, str]] = {}
        status_code: Optional[int] = None
        body: Optional[StreamInterface] = None

        """
        self._responses: BatchResponseContent = BatchResponseContent()

    def add_response(self, content: Optional[BatchResponseItem] = None) -> None:
        # loop through items in content adding each to responses
        self._responses.responses = [item for item in content]

    async def get_response_by_id(self, request_id: str) -> Optional[BatchResponseItem]:
        """
        Get a response by its request ID from the collection        
        :param request_id: The request ID of the response to get
        :type request_id: str
        :return: The response with the specified request ID as a BatchResponseItem
        :rtype: Optional[BatchResponseItem]
        """
        if not self._responses:
            raise ValueError("No responses found in the collection")
        if (isinstance(self._responses, BatchResponseContent)):
            for response in self._responses.responses:
                if isinstance(response, BatchResponseItem) and response.id == request_id:
                    return response
        raise TypeError("Invalid type: Collection must be of type BatchResponseContent")

    @property
    async def responses_status_codes(self) -> Dict[str, int]:
        status_codes: Dict[str, int] = {}
        for response in self._responses:
            if (isinstance(response, BatchResponseItem)):
                status_codes[response.id] = response.status_code
            raise TypeError("Invalid type: Collection must be of type BatchResponseContent")
        return status_codes

    def get_field_deserializers(self) -> Dict[str, Callable[[ParseNode], None]]:
        return {
            'responses':
            lambda n: setattr(
                self, "_responses", n.get_collection_of_object_values(BatchResponseItem.create)
            )
        }

    def serialize(self, writer: SerializationWriter) -> None:
        writer.write_collection_of_object_values('responses', self._responses.values())
