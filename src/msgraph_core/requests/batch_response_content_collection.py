from typing import Optional, Dict, Callable, List

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
        self._responses: List[BatchResponseContent] = []

    def add_response(self, response: BatchResponseContent) -> None:
        """ 
        Adds a response to the collection.
        Args:
            keys: The keys of the response to add.
            response: The response to add.
        """
        self._responses.append(response)

    def get_responses(self):
        """ 
        Gets the responses in the collection.
        Returns:
            List[Tuple[str, BatchResponseContent]]: The responses in the collection.
        """
        return self._responses

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
