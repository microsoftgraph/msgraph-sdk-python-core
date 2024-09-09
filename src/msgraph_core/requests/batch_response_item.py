from typing import Optional, Dict, Any
from io import BytesIO

from kiota_abstractions.serialization import Parsable
from kiota_abstractions.serialization import ParseNode
from kiota_abstractions.serialization import SerializationWriter


class StreamInterface(BytesIO):  # move to helpers
    pass


class BatchResponseItem(Parsable):

    def __init__(self) -> None:
        """
        Initializes a new instance of the BatchResponseItem class.
        """
        self._id: Optional[str] = None
        self._atomicity_group: Optional[str] = None
        self._status_code: Optional[int] = None
        self._headers: Optional[Dict[str, str]] = {}
        self._body: Optional[StreamInterface] = None

    @staticmethod
    def create(parse_node: ParseNode) -> 'BatchResponseItem':
        """
        Creates a new instance of the BatchResponseItem class.
        """
        return BatchResponseItem()

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
    def status_code(self) -> Optional[int]:
        """
        Get the status code of the response
        :return: The status code of the response
        :rtype: Optional[int]
        """
        return self._status_code

    @status_code.setter
    def status_code(self, status_code: Optional[int]) -> None:
        """ 
        Set the status code of the response
        :param status_code: The status code of the response
        :type status_code: Optional[int]
        """
        self._status_code = status_code

    @property
    def headers(self) -> Optional[Dict[str, str]]:
        """
        Get the headers of the response
        :return: The headers of the response
        :rtype: Optional[Dict[str, str]]
        """
        return self._headers

    @headers.setter
    def headers(self, headers: Optional[Dict[str, str]]) -> None:
        """
        Set the headers of the response
        :param headers: The headers of the response
        :type headers: Optional[Dict[str, str]]
        """
        self._headers = headers

    @property
    def body(self) -> Optional[StreamInterface]:
        """
        Get the body of the response
        :return: The body of the response
        :rtype: Optional[StreamInterface]
        """
        return self._body

    @body.setter
    def body(self, body: Optional[StreamInterface]) -> None:
        """
        Set the body of the response
        :param body: The body of the response
        :type body: Optional[StreamInterface]
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
        # if parse_node is None:
        #     raise ValueError("parse_node cannot be None")
        return BatchResponseItem(
            id=parse_node.get_str_value("id"),
            status=parse_node.get_int_value("status"),
            headers=parse_node.get_object_value(lambda n: n.get_str_value()),
            body=parse_node.get_object_value(lambda n: n.get_object_value(lambda x: x))
        )

    def get_field_deserializers(self) -> Dict[str, Any]:
        """
        Gets the deserialization information for this object.

        """
        return {
            "id": lambda n: setattr(self, "id", n.get_str_value()),
            'atomicity_group': lambda n: setattr(self, "atomicity_group", n.get_str_value()),
            'status_code': lambda n: setattr(self, "status_code", n.get_int_value()),
            'headers': lambda n: setattr(self, "headers", n.get_collection_of_primitive_values()),
            'body': lambda n: setattr(self, "body", n.get_bytes_value()),
        }

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Writes the objects properties to the current writer.
        """
        writer.write_str_value('id', self._id)
        writer.write_str_value('atomicity_group', self._atomicity_group)
        writer.write_int_value('status_code', self._status_code)
        writer.write_collection_of_primitive_values('headers', self._headers)
        writer.write_bytes_value('body', self._body)
