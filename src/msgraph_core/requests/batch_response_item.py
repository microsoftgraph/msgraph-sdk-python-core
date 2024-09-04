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
        return BatchResponseItem()

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, id: Optional[str]) -> None:
        self._id = id

    @property
    def atomicity_group(self) -> Optional[str]:
        return self._atomicity_group

    @atomicity_group.setter
    def atomicity_group(self, atomicity_group: Optional[str]) -> None:
        self._atomicity_group = atomicity_group

    @property
    def status_code(self) -> Optional[int]:
        return self._status_code

    @status_code.setter
    def status_code(self, status_code: Optional[int]) -> None:
        self._status_code = status_code

    @property
    def headers(self) -> Optional[Dict[str, str]]:
        return self._headers

    @headers.setter
    def headers(self, headers: Optional[Dict[str, str]]) -> None:
        self._headers = headers

    @property
    def body(self) -> Optional[StreamInterface]:
        return self._body

    @body.setter
    def body(self, body: Optional[StreamInterface]) -> None:
        self._body = body

    @property
    def content_type(self) -> Optional[str]:
        if self.headers:
            headers = {k.lower(): v for k, v in self.headers.items()}
            return headers.get('content-type')
        return None

    def get_field_deserializers(self) -> Dict[str, Any]:
        return {
            "@odata.nextLink": lambda x: setattr(self, "odata_next_link", x.get_str_value()),
            "id": lambda n: setattr(self, "id", n.get_str_value()),
            'atomicity_group': lambda n: setattr(self, "atomicity_group", n.get_str_value()),
            'status_code': lambda n: setattr(self, "status_code", n.get_int_value()),
            'headers': lambda n: setattr(self, "headers", n.get_collection_of_primitive_values()),
            'body': lambda n: setattr(self, "body", n.get_bytes_value()),
        }

    def serialize(self, writer: SerializationWriter) -> None:
        writer.write_str_value('id', self._id)
        writer.write_str_value('atomicity_group', self._atomicity_group)
        writer.write_int_value('status_code', self._status_code)
        writer.write_collection_of_primitive_values('headers', self._headers)
        writer.write_bytes_value('body', self._body)
