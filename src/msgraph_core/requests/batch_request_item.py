import base64
import enum
import json
import re
import urllib.request
from io import BytesIO
from typing import Any, Optional, Union
from urllib.parse import urlparse
from uuid import uuid4
from deprecated import deprecated

from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders
from kiota_abstractions.method import Method
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter


@deprecated("Use BytesIO type instead")
class StreamInterface(BytesIO):
    pass


class BatchRequestItem(Parsable):
    API_VERSION_REGEX = re.compile(r'/\/(v1.0|beta)/')
    ME_TOKEN_REGEX = re.compile(r'/\/users\/me-token-to-replace/')

    def __init__(
        self,
        request_information: Optional[RequestInformation] = None,
        id: str = "",
        depends_on: Optional[list[Union[str, 'BatchRequestItem']]] = []
    ):
        """
        Initializes a new instance of the BatchRequestItem class.
        Args:
            request_information (RequestInformation): The request information.
            id (str, optional): The ID of the request item. Defaults to "".
            depends_on (Optional[list[Union[str, BatchRequestItem]], optional):
            The IDs of the requests that this request depends on. Defaults to None.
        """
        if request_information is None or not request_information.http_method:
            raise ValueError("HTTP method cannot be Null/Empty")
        self._id = id or str(uuid4())
        if isinstance(request_information.http_method, enum.Enum):
            self._method = request_information.http_method.name
        else:
            self._method = request_information.http_method
        self._headers: Optional[dict[str, str]] = request_information.request_headers
        self._body = request_information.content
        self.url = request_information.url.replace('/users/me-token-to-replace', '/me', 1)
        self._depends_on: Optional[list[str]] = []
        if depends_on is not None:
            self.set_depends_on(depends_on)

    @staticmethod
    def create_with_urllib_request(
        request: urllib.request.Request,
        id: str = "",
        depends_on: Optional[list[str]] = None
    ) -> 'BatchRequestItem':
        """
        Creates a new instance of the BatchRequestItem class from a urllib request.
        Args:
            request (urllib.request.Request): The urllib request.
            id (str, optional): The ID of the request item. Defaults to "".
            depends_on (Optional[list[str]], optional): The IDs of
                 the requests that this request depends on. Defaults to None.
        Returns:
            BatchRequestItem: A new instance of the BatchRequestItem class.
        """
        request_info = RequestInformation()
        try:
            request_info.http_method = Method[request.get_method().upper()]
        except KeyError:
            raise KeyError(f"Request Method: {request.get_method()} is invalid")

        request_info.url = request.full_url
        request_info.headers = RequestHeaders()
        for key, value in request.headers.items():
            request_info.headers.try_add(header_name=key, header_value=value)
        request_info.content = request.data  # type: ignore
        return BatchRequestItem(
            request_info,
            id,
            depends_on  # type: ignore # union types not analysed correctly
        )

    def set_depends_on(self, requests: Optional[list[Union[str, 'BatchRequestItem']]]) -> None:
        """
        Sets the IDs of the requests that this request depends on.
        Args:
            requests (Optional[list[Union[str, BatchRequestItem]]): The
                IDs of the requests that this request depends on.
        """
        if requests:
            for request in requests:
                if self._depends_on is None:
                    self._depends_on = []
                self._depends_on.append(request if isinstance(request, str) else request.id)

    def set_url(self, url: str) -> None:
        """
        Sets the URL of the request.
        Args:
            url (str): The URL of the request.
        """
        url_parts = urlparse(url)
        if not url_parts.path:
            raise ValueError(f"Invalid URL {url}")

        relative_url = re.sub(BatchRequestItem.API_VERSION_REGEX, '', url_parts.path, 1)
        if not relative_url:
            raise ValueError(
                f"Error occurred during regex replacement of API version in URL string: {url}"
            )

        relative_url = relative_url.replace('/users/me-token-to-replace', '/me', 1)
        if not relative_url:
            raise ValueError(
                f"""Error occurred during regex replacement
                of '/users/me-token-to-replace' in URL string: {url}"""
            )
        self.url = relative_url
        if url_parts.query:
            self.url += f"?{url_parts.query}"
        if url_parts.fragment:
            self.url += f"#{url_parts.fragment}"

    @property
    def id(self) -> str:
        """
        Gets the ID of the request item.
        Returns:
            str: The ID of the request item.
        """
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        """
        Sets the ID of the request item.
        Args:
            value (str): The ID of the request item.
        """
        self._id = value

    @property
    def headers(self) -> Optional[dict[str, str]]:
        """
        Gets the headers of the request item.
        Returns:
            Optional[dict[str, str]]: The headers of the request item.
        """
        return self._headers

    @headers.setter
    def headers(self, headers: dict[str, Union[list[str], str]]) -> None:
        """
        Sets the headers of the request item.
        Args:
            headers (dict[str, Union[list[str], str]]): The headers of the request item.
        """
        if self._headers:
            self._headers.clear()
        else:
            self._headers = {}
        headers_collection = RequestHeaders()
        for header, value in headers.items():
            headers_collection.add(header, value)
        for key, values in headers_collection.get_all().items():
            self._headers[key] = ', '.join(values)

    @property
    def body(self) -> Optional[bytes]:
        """
        Gets the body of the request item.
        Returns:
            Optional[bytes]: The body of the request item.
        """
        return self._body

    @body.setter
    def body(self, body: BytesIO) -> None:
        """
        Sets the body of the request item.
        Args:
            body : (BytesIO): The body of the request item.
        """
        self._body = body.getvalue()

    @property
    def method(self) -> str:
        """
        Gets the HTTP method of the request item.
        Returns:
            str: The HTTP method of the request item.
        """
        return self._method

    @method.setter
    def method(self, value: str) -> None:
        """
        Sets the HTTP method of the request item.
        Args:
            value (str): The HTTP method of the request item.

        """

        self._method = value

    @property
    def depends_on(self) -> Optional[list[str]]:
        """
        Gets the IDs of the requests that this request depends on.
        Returns:
            Optional[list[str]]: The IDs of the requests that this request depends on.
        """
        return self._depends_on

    @staticmethod
    def create_from_discriminator_value(
        parse_node: Optional[ParseNode] = None
    ) -> 'BatchRequestItem':
        """
        Creates a new instance of the appropriate class based
        on discriminator value param parse_node: The parse node
        to use to read the discriminator value and create the object
        Returns: BatchRequestItem
        """
        if not parse_node:
            raise TypeError("parse_node cannot be null.")
        return BatchRequestItem()

    def get_field_deserializers(self) -> dict[str, Any]:
        """
        Gets the deserialization information for this object.
        Returns:
            dict[str, Any]: The deserialization information for
            this object where each entry is a property key with its
             deserialization callback.
        """
        return {
            "id": self._id,
            "method": self.method,
            "url": self.url,
            "headers": self._headers,
            "body": self._body,
            "depends_on": self._depends_on
        }

    def serialize(self, writer: SerializationWriter) -> None:
        """
        Writes the objects properties to the current writer.
        Args:
            writer (SerializationWriter): The writer to write to.
        """
        writer.write_str_value('id', self.id)
        writer.write_str_value('method', self.method)
        writer.write_str_value('url', self.url)
        writer.write_collection_of_primitive_values('depends_on', self._depends_on)
        writer.write_additional_data_value(
            {'headers': self._headers}  # need proper method to serialize dicts
        )
        if self._body:
            json_object = json.loads(self._body)
            is_json_string = json_object and isinstance(json_object, dict)
            # /$batch API expects JSON object or base 64 encoded value for the body
            if is_json_string:
                writer.write_additional_data_value(
                    {'body': json_object}  # need proper method to serialize dicts
                )
            else:
                writer.write_str_value('body', base64.b64encode(self._body).decode('utf-8'))
