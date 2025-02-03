import base64
from collections.abc import Callable
from io import BytesIO
from typing import Optional, Type, TypeVar, Union

from kiota_abstractions.serialization import (
    Parsable,
    ParsableFactory,
    ParseNode,
    ParseNodeFactoryRegistry,
    SerializationWriter,
)

from .batch_response_item import BatchResponseItem

T = TypeVar('T', bound=ParsableFactory)


class BatchResponseContent(Parsable):

    def __init__(self) -> None:
        """
        Initializes a new instance of the BatchResponseContent class.
        BatchResponseContent is a collection of BatchResponseItem items,
         each with a unique request ID.
        """
        self._responses: Optional[dict[str, BatchResponseItem]] = {}

    @property
    def responses(self) -> Optional[dict[str, BatchResponseItem]]:
        """
        Get the responses in the collection
        :return: A dictionary of response IDs and their BatchResponseItem objects
        :rtype: Optional[dict[str, BatchResponseItem]]
        """
        return self._responses

    @responses.setter
    def responses(self, responses: Optional[dict[str, BatchResponseItem]]) -> None:
        """
        Set the responses in the collection
        :param responses: The responses to set in the collection
        :type responses: Optional[dict[str, BatchResponseItem]]
        """
        self._responses = responses

    def get_response_by_id(
        self,
        request_id: str,
        response_type: Optional[Type[T]] = None,
    ) -> Optional[Union[T, BatchResponseItem]]:
        """
        Get a response by its request ID from the collection
        :param request_id: The request ID of the response to get
        :type request_id: str
        :return: The response with the specified request ID as a BatchResponseItem
        :rtype: BatchResponseItem
        """
        if self._responses is None:
            return None
        if response_type is not None:
            return self.response_body(request_id, response_type)
        return self._responses.get(request_id)

    def get_response_stream_by_id(self, request_id: str) -> Optional[BytesIO]:
        """
        Get a response by its request ID and return the body as a stream
        :param request_id: The request ID of the response to get
        :type request_id: str
        :return: The response Body as a stream
        :rtype: BytesIO
        """
        response_item = self.get_response_by_id(request_id)
        if response_item is None or response_item.body is None:
            return None

        if isinstance(response_item.body, BytesIO):
            return response_item.body
        return BytesIO(response_item.body)

    def get_response_status_codes(self) -> dict[str, int]:
        """
        Go through responses and for each, append {'request-id': status_code} to a dictionary.
        :return: A dictionary with request_id as keys and status_code as values.
        :rtype: dict
        """
        status_codes: dict[str, int] = {}
        if self._responses is None:
            return status_codes

        for request_id, response_item in self._responses.items():
            if response_item is not None and response_item.status is not None:
                status_codes[request_id] = response_item.status

        return status_codes

    def response_body(self, request_id: str, type: Type[T]) -> Optional[T]:
        """
        Get the body of a response by its request ID from the collection
        :param request_id: The request ID of the response to get
        :type request_id: str
        :param type: The type to deserialize the response body to
        :type type: Type[T]
        :return: The deserialized response body
        :rtype: Optional[T]
        """
        if not self._responses or request_id not in self._responses:
            raise ValueError(f"No response found for id: {request_id}")

        if not issubclass(type, Parsable):
            raise ValueError("Type passed must implement the Parsable interface")

        response = self.get_response_by_id(request_id)
        if response is not None:
            content_type = response.content_type
        else:
            raise ValueError(
                f"Unable to get content-type header in response item for request Id: {request_id}"
            )
        if not content_type:
            raise RuntimeError("Unable to get content-type header in response item")

        response_body = response.body or BytesIO()
        try:
            try:
                parse_node = ParseNodeFactoryRegistry().get_root_parse_node(
                    content_type, response_body
                )
            except Exception:
                response_body.seek(0)
                base64_decoded_body = BytesIO(base64.b64decode(response_body.read()))
                parse_node = ParseNodeFactoryRegistry().get_root_parse_node(
                    content_type, base64_decoded_body
                )
                response.body = base64_decoded_body
            return parse_node.get_object_value(type)
        except Exception:
            raise ValueError(
                f"Unable to deserialize batch response for request Id: {request_id} to {type}"
            )

    def get_field_deserializers(self) -> dict[str, Callable[[ParseNode], None]]:
        """
        Gets the deserialization information for this object.
        :return: The deserialization information for this object
        :rtype: dict[str, Callable[[ParseNode], None]]
        """

        def set_responses(n: ParseNode):
            values = n.get_collection_of_object_values(BatchResponseItem)
            if values:
                setattr(self, '_responses', {item.id: item for item in values})
            else:
                setattr(self, '_responses', {})

        return {'responses': lambda n: set_responses(n)}

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Writes the objects properties to the current writer.
        :param writer: The writer to write to
        """
        if self._responses is not None:
            writer.write_collection_of_object_values('responses', list(self._responses.values()))
        else:
            writer.write_collection_of_object_values('responses', [])

    @staticmethod
    def create_from_discriminator_value(
        parse_node: Optional[ParseNode] = None
    ) -> 'BatchResponseContent':
        if parse_node is None:
            raise ValueError("parse_node cannot be None")
        return BatchResponseContent()
