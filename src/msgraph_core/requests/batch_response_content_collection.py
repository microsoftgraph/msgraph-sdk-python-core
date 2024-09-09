from typing import Optional, Dict, Callable

from kiota_abstractions.serialization import Parsable
from kiota_abstractions.serialization import ParseNode
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
        """ 
        Add a response to the collection
        :param content: The response to add to the collection
        :type content: Optional[BatchResponseItem]
        """
        if content is None:
            return
        for item in content:
            self._responses.responses = content

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
        if isinstance(self._responses, BatchResponseContent):
            if self._responses.responses is None:
                raise ValueError("No responses found in the collection")
            for response in self._responses.responses:
                if isinstance(response, BatchResponseItem) and response.id == request_id:
                    return response
        raise TypeError("Invalid type: Collection must be of type BatchResponseContent")

    @property
    async def responses_status_codes(self) -> Dict[str, int]:
        """
        Get the status codes of all responses in the collection
        :return: A dictionary of response IDs and their status codes
        :rtype: Dict[str, int]
        """
        status_codes: Dict[str, int] = {}
        for response in self._responses:
            if isinstance(response, BatchResponseItem):
                if response.id is not None:
                    status_codes[response.id] = response.status_code
                else:
                    raise ValueError("Response ID cannot be None")
            else:
                raise TypeError("Invalid type: Collection must be of type BatchResponseContent")
        return status_codes

    def get_field_deserializers(self) -> Dict[str, Callable[[ParseNode], None]]:
        """ 
        Gets the deserialization information for this object.
        :return: The deserialization information for this object where each entry is a property key
        with its deserialization callback.
        :rtype: Dict[str, Callable[[ParseNode], None]]
        """
        return {
            'responses':
            lambda n: setattr(
                self, "_responses",
                n.
                get_collection_of_object_values(BatchResponseItem.create_from_discriminator_value)
            )
        }

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Writes the objects properties to the current writer.
        :param writer: The writer to write to.
        :type writer: SerializationWriter
        """
        writer.write_collection_of_object_values('responses', self._responses)
