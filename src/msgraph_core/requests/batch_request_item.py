from typing import List, Optional, Dict, Callable

from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import Parsable
from kiota_abstractions.serialization import SerializationWriter


class BatchRequestItem(Parsable):

    def __init__(
        self,
        request_information: RequestInformation,
        id: str = "",
        depends_on: Optional[List[str]] = None
    ):
        pass

    def depends_on(self, requests: Optional[List[str]]) -> None:
        pass

    def set_url(self, url: str) -> None:
        pass

    def get_id(self) -> str:
        pass

    @property
    def id(self) -> str:
        pass

    @property
    def headers() -> List[RequestHeaders]:
        pass

    @property
    def body(self) -> None:
        pass

    @property
    def method(self) -> str:
        pass

    @property
    def depends_on(self) -> List[str]:
        pass

    def get_field_deserializers(self) -> Dict[str, Callable]:
        pass

    def serialize(self, writer: SerializationWriter) -> None:
        pass
