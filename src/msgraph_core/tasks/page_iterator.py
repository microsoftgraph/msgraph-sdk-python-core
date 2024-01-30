from typing import Callable, Optional, Union

from requests import Session
from requests.exceptions import InvalidURL

from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.method import Method
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders
from kiota_abstractions.serialization.parsable import Parsable

from ..models import PageResult

T = TypeVar('T')


class PageIterator:

    def __init__(
        self,
        response: Union[T, list, object],
        request_adapter: Session,
        constructor_callable: Optional[Callable] = None
    ):
        self.request_adapter = request_adapter
        self.constructor_callable = constructor_callable or (lambda x: x)
        self.pause_index = 0
        self.headers = {}
        self.request_options = []
        self.current_page = self.convert_to_page(response)
        self.has_next = bool(self.current_page['value'])

    def set_headers(self, headers: dict) -> None:
        self.headers.update(headers)

    def set_request_options(self, request_options: list) -> None:
        self.request_options = request_options

    def set_pause_index(self, pause_index: int) -> None:
        self.pause_index = pause_index

    def iterate(self, callback: Callable) -> None:
        pass

    def next(self) -> Optional[dict]:
        pass

    @staticmethod
    def convert_to_page(response: Union[T, list, object]) -> dict:
        pass

    def fetch_next_page(self) -> dict:
        pass

    def enumerate(self, callback: Optional[Callable] = None) -> bool:
        pass

    def has_next(self) -> bool:
        return self.has_next
