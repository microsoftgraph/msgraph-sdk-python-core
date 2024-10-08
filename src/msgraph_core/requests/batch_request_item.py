import re
import enum
import json
from uuid import uuid4
from typing import List, Optional, Dict, Union, Any
from io import BytesIO
import base64
import urllib.request
from urllib.parse import urlparse

from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import Parsable
from kiota_abstractions.serialization import SerializationWriter
from kiota_abstractions.serialization import ParseNode


class StreamInterface(BytesIO):
    pass


class BatchRequestItem(Parsable):
    API_VERSION_REGEX = re.compile(r'/\/(v1.0|beta)/')
    ME_TOKEN_REGEX = re.compile(r'/\/users\/me-token-to-replace/')

    def __init__(
        self,
        request_information: Optional[RequestInformation] = None,
        id: str = "",
        depends_on: Optional[List[Union[str, 'BatchRequestItem']]] = []
    ):
        """ 
        Initializes a new instance of the BatchRequestItem class.
        Args:
            request_information (RequestInformation): The request information.
            id (str, optional): The ID of the request item. Defaults to "".
            depends_on (Optional[List[Union[str, BatchRequestItem]], optional):
            The IDs of the requests that this request depends on. Defaults to None.
        """
        if request_information is None or not request_information.http_method:
            raise ValueError("HTTP method cannot be Null/Empty")
        self._id = id or str(uuid4())
        if isinstance(request_information.http_method, enum.Enum):
            self._method = request_information.http_method.name
        else:
            self._method = request_information.http_method
        self._headers = request_information.request_headers
        self._body = request_information.content
        self.url = request_information.url.replace('/users/me-token-to-replace', '/me', 1)
        self._depends_on: Optional[List[str]] = []
        if depends_on is not None:
            self.set_depends_on(depends_on)

    @staticmethod
    def create_with_urllib_request(
        request: urllib.request.Request,
        id: str = "",
        depends_on: Optional[List[str]] = None
    ) -> 'BatchRequestItem':
        """ 
        Creates a new instance of the BatchRequestItem class from a urllib request.
        Args:
            request (urllib.request.Request): The urllib request.
            id (str, optional): The ID of the request item. Defaults to "".
            depends_on (Optional[List[str]], optional): The IDs of
                 the requests that this request depends on. Defaults to None.
        Returns:    
            BatchRequestItem: A new instance of the BatchRequestItem class.
        """
        request_info = RequestInformation()
        request_info.http_method = request.get_method()
        request_info.url = request.full_url
        request_info.headers = RequestHeaders()
        for key, value in request.headers.items():
            request_info.headers.try_add(header_name=key, header_value=value)
        request_info.content = request.data
        return BatchRequestItem(request_info, id, depends_on)

    def set_depends_on(self, requests: Optional[List[Union[str, 'BatchRequestItem']]]) -> None:
        """
        Sets the IDs of the requests that this request depends on.
        Args:
            requests (Optional[List[Union[str, BatchRequestItem]]): The 
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
    def headers(self) -> List[RequestHeaders]:
        """
        Gets the headers of the request item.
        Returns:
            List[RequestHeaders]: The headers of the request item.
        """
        return self._headers

    @headers.setter
    def headers(self, headers: Dict[str, Union[List[str], str]]) -> None:
        """
        Sets the headers of the request item.
        Args:
            headers (Dict[str, Union[List[str], str]]): The headers of the request item.
        """
        self._headers.clear()
        self._headers.update(headers)

    @property
    def body(self) -> None:
        """
        Gets the body of the request item.
        Returns:
            None: The body of the request item.
        """
        return self._body

    @body.setter
    def body(self, body: BytesIO) -> None:
        """
        Sets the body of the request item.
        Args:
            body : (BytesIO): The body of the request item.
        """
        self._body = body

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
    def depends_on(self) -> Optional[List[str]]:
        """
        Gets the IDs of the requests that this request depends on.
        Returns:
            Optional[List[str]]: The IDs of the requests that this request depends on.
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

    def get_field_deserializers(self) -> Dict[str, Any]:
        """ 
        Gets the deserialization information for this object.
        Returns:
            Dict[str, Any]: The deserialization information for 
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
        headers = {key: ", ".join(val) for key, val in self._headers.items()}
        writer.write_collection_of_object_values('headers', headers)
        if self._body:
            json_object = json.loads(self._body)
            is_json_string = json_object and isinstance(json_object, dict)
            writer.write_collection_of_object_values(
                'body',
                json_object if is_json_string else base64.b64encode(self._body).decode('utf-8')
            )
