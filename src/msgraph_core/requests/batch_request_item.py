import re
import json
from uuid import uuid4
from typing import List, Optional, Dict, Callable, Union, Any
from io import BytesIO
import base64
import urllib.request
from urllib.parse import urlparse

from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import Parsable
from kiota_abstractions.serialization import SerializationWriter


class StreamInterface(BytesIO):
    pass


# request headers and request information are imported, streaIterfac and serialization writer too
class BatchRequestItem(Parsable):
    API_VERSION_REGEX = re.compile(r'/\/(v1.0|beta)/')
    ME_TOKEN_REGEX = re.compile(r'/\/users\/me-token-to-replace/')

    def __init__(
        self,
        request_information: RequestInformation,
        id: str = "",
        depends_on: Optional[List[Union[str, 'BatchRequestItem']]] = None
    ):
        if not request_information.http_method:
            raise ValueError("HTTP method cannot be Null/Empty")
        self._id = id or str(uuid4())
        self.method = request_information.http_method
        self._headers = request_information.request_headers
        self._body = request_information.content
        self.url = request_information.url
        self._depends_on: Optional[List[str]] = []
        self.set_depends_on(depends_on)

    @staticmethod
    def create_with_urllib_request(
        request: urllib.request.Request,
        id: str = "",
        depends_on: Optional[List[str]] = None
    ) -> 'BatchRequestItem':
        request_info = RequestInformation()
        request_info.http_method = request.get_method()
        request_info.url = request.full_url
        request_info.headers = dict(request.header_items())
        request_info.content = request.data
        return BatchRequestItem(request_info, id, depends_on)

    def set_depends_on(self, requests: Optional[List[Union[str, 'BatchRequestItem']]]) -> None:
        if requests:
            for request in requests:
                self._depends_on.append(request if isinstance(request, str) else request.id)

    def set_url(self, url: str) -> None:
        url_parts = urlparse(url)
        if not url_parts.path:
            raise ValueError(f"Invalid URL {url}")

        relative_url = re.sub(BatchRequestItem.API_VERSION_REGEX, '', url_parts.path, 1)
        if not relative_url:
            raise ValueError(
                f"Error occurred during regex replacement of API version in URL string: {url}"
            )

        relative_url = re.sub(self.ME_TOKEN_REGEX, '/me', relative_url, 1)
        if not relative_url:
            raise ValueError(
                f"Error occurred during regex replacement of '/users/me-token-to-replace' in URL string: {url}"
            )

        self.url = relative_url
        if url_parts.query:
            self.url += f"?{url_parts.query}"
        if url_parts.fragment:
            self.url += f"#{url_parts.fragment}"

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def headers(self) -> List[RequestHeaders]:
        return self._headers

    @headers.setter
    def headers(self, headers: Dict[str, Union[List[str], str]]) -> None:
        self._headers.clear()
        self._headers.update(headers)

    @property
    def body(self) -> None:
        return self._body

    @body.setter
    def body(self, body: Optional[StreamInterface]) -> None:
        self._body = body

    @property
    def method(self) -> str:
        return self._method

    @method.setter
    def method(self, value: str) -> None:
        self._method = value

    @property
    def depends_on(self) -> Optional[List[str]]:
        return self._depends_on

    def get_field_deserializers(self) -> Dict[str, Any]:
        return {}

    def serialize(self, writer: SerializationWriter) -> None:
        writer.write_str_value('id', self.id)
        writer.write_str_value('method', self.method)
        writer.write_str_value('url', self.url)
        writer.write_collection_of_primitive_values('depends_on', self._depends_on)
        headers = {key: ", ".join(val) for key, val in self._headers.items()}
        writer.write_additional_data_value('headers', headers)
        if self._body:
            json_object = json.loads(self._body.read())
            is_json_string = json_object and isinstance(json_object, dict)
            self.body.seek(0)
            writer.write_additional_data_value(
                'body', json_object
                if is_json_string else base64.b64encode(self._body.read()).decode('utf-8')
            )
