from io import BytesIO
from typing import Callable, Optional

from deprecated import deprecated
from kiota_abstractions.serialization import (
    Parsable,
    ParsableFactory,
    ParseNode,
    SerializationWriter,
)


@deprecated("Use BytesIO type instead")
class StreamInterface(BytesIO):
    pass


class BatchResponseItem(Parsable):

    def __init__(self) -> None:
        """
        Initializes a new instance of the BatchResponseItem class.
        """
        self._id: Optional[str] = None
        self._atomicity_group: Optional[str] = None
        self._status: Optional[int] = None
        self._headers: Optional[dict[str, str]] = {}
        self._body: Optional[BytesIO] = None

    @property
    def id(self) -> Optional[str]:
        """
        Get the ID of the response
        :return: The ID of the response
        :rtype: Optional[str]
        """
        return self._id

    @id.setter
    def id(self, id: Optional[str]) -> None:
        """
        Set the ID of the response
        :param id: The ID of the response
        :type id: Optional[str]
        """
        self._id = id

    @property
    def atomicity_group(self) -> Optional[str]:
        """
        Get the atomicity group of the response
        :return: The atomicity group of the response
        :rtype: Optional[str]
        """
        return self._atomicity_group

    @atomicity_group.setter
    def atomicity_group(self, atomicity_group: Optional[str]) -> None:
        """
        Set the atomicity group of the response
        :param atomicity_group: The atomicity group of the response
        :type atomicity_group: Optional[str]
        """
        self._atomicity_group = atomicity_group

    @property
    def status(self) -> Optional[int]:
        """
        Get the status code of the response
        :return: The status code of the response
        :rtype: Optional[int]
        """
        return self._status

    @status.setter
    def status(self, status_code: Optional[int]) -> None:
        """
        Set the status code of the response
        :param status_code: The status code of the response
        :type status_code: Optional[int]
        """
        self._status = status_code

    @property
    def headers(self) -> Optional[dict[str, str]]:
        """
        Get the headers of the response
        :return: The headers of the response
        :rtype: Optional[dict[str, str]]
        """
        return self._headers

    @headers.setter
    def headers(self, headers: Optional[dict[str, str]]) -> None:
        """
        Set the headers of the response
        :param headers: The headers of the response
        :type headers: Optional[dict[str, str]]
        """
        self._headers = headers

    @property
    def body(self) -> Optional[BytesIO]:
        """
        Get the body of the response
        :return: The body of the response
        :rtype: Optional[BytesIO]
        """
        return self._body

    @body.setter
    def body(self, body: Optional[BytesIO]) -> None:
        """
        Set the body of the response
        :param body: The body of the response
        :type body: Optional[BytesIO]
        """
        self._body = body

    @property
    def content_type(self) -> Optional[str]:
        """
        Get the content type of the response
        :return: The content type of the response
        :rtype: Optional[str]
        """
        if self.headers:
            headers = {k.lower(): v for k, v in self.headers.items()}
            return headers.get('content-type')
        return None

    @staticmethod
    def create_from_discriminator_value(
        parse_node: Optional[ParseNode] = None
    ) -> 'BatchResponseItem':
        """
        Creates a new instance of the appropriate class based on discriminator value
        Args:
            parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BatchResponseItem
        """
        if not parse_node:
            raise TypeError("parse_node cannot be null")
        return BatchResponseItem()

    def get_field_deserializers(self) -> dict[str, Callable[[ParseNode], None]]:
        """
        Gets the deserialization information for this object.

        """
        return {
            "id": lambda x: setattr(self, "id", x.get_str_value()),
            "status": lambda x: setattr(self, "status", x.get_int_value()),
            "headers": lambda x: setattr(
                self,
                "headers",
                x.try_get_anything(x._json_node)  # type: ignore
            ),  # need interface to return a dictionary
            "body": lambda x: setattr(self, "body", x.get_bytes_value()),
        }

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Writes the objects properties to the current writer.
        """
        writer.write_str_value('id', self._id)
        writer.write_str_value('atomicity_group', self._atomicity_group)
        writer.write_int_value('status', self._status)
        writer.write_collection_of_primitive_values(
            'headers',
            self._headers  # type: ignore
        )  # need method to serialize dicts
        if self._body:
            writer.write_bytes_value('body', self._body.getvalue())
        else:
            writer.write_bytes_value('body', None)
