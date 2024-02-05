from typing import Callable, Optional, Union

from typing import TypeVar
from requests.exceptions import InvalidURL

from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.method import Method
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders # Use for headers
from kiota_abstractions.serialization.parsable import Parsable

from models import PageResult

T = TypeVar('T', bound=Parsable)


class PageIterator:

    def __init__(
        self,
        response: Union[T, list, object],
        request_adapter: RequestAdapter,
        constructor_callable: Optional[Callable] = None
    ):
        self.request_adapter = request_adapter
        self.constructor_callable = constructor_callable or (lambda x: x)
        self.pause_index = 0
        self.headers = {}
        self.request_options = []  # check implementation of RequestOption and apply use it here
        self.current_page = self.convert_to_page(response)
        self.has_next = bool(self.current_page.odata_next_link)
        # self.current_page.get('@odata.nextLink')


    def set_headers(self, headers: dict) -> None:
        self.headers.update(**headers)

    def set_request_options(self, request_options: list) -> None:
        self.request_options = request_options

    def set_pause_index(self, pause_index: int) -> None:
        self.pause_index = pause_index

    def iterate(self, callback: Callable) -> None:
        while True:
            keep_iterating = self.enumerate(callback)
            if not keep_iterating:
                return
            next_page = self.next()
            if not next_page:
                return
            self.current_page = next_page
            self.pause_index = 0

    def next(self) -> Optional[dict]:
        if not self.current_page.odata_next_link:
            return None
        response = self.fetch_next_page()
        return self.convert_to_page(response)

    @staticmethod
    def convert_to_page(response: Union[T, list, object]) -> PageResult:
        if not response:
            raise ValueError('Response cannot be null.')
        value = None
        if isinstance(response, list):
            value = response.get('value', [])
        elif hasattr(response, 'value'):
            value = getattr(response, 'value')
        elif isinstance(response, object):
            value = getattr(response, 'value', [])
        if value is None:
            raise ValueError('The response does not contain a value.')
        parsable_page = response if isinstance(response, dict) else vars(response)
        next_link = parsable_page.get('@odata.nextLink', '') if isinstance(
            parsable_page, dict
        ) else getattr(parsable_page, '@odata.nextLink', '')
        page = PageResult()
        page.odata_next_link = next_link
        page.set_value(value)
        return page

    def fetch_next_page(self) -> dict:
        error_map = {
            400: 'BadRequestError',
            401: 'UnauthorizedError',
            403: 'ForbiddenError',
            404: 'NotFoundError',
        }
        next_link = self.current_page.odata_next_link
        if not next_link:
            raise ValueError('The response does not contain a nextLink.')
        if not next_link.startswith('http'):
            raise InvalidURL('Could not parse nextLink URL.')
        request_info = RequestInformation()
        request_info.http_method = Method.GET
        request_info.url = next_link
        request_info.headers = self.headers
        if self.request_options:
            request_info.add_request_options(*self.request_options)
            
        response = self.request_adapter.send_async(request_info, self.constructor_callable, error_map)
        return response

    def enumerate(self, callback: Optional[Callable] = None) -> bool:
        keep_iterating = True
        page_items = self.current_page.value or  []
        if not page_items:
            return False
        for i in range(self.pause_index, len(page_items)):
            keep_iterating = callback(page_items[i]) if callback else True
            if not keep_iterating:
                self.pause_index = i + 1
                break