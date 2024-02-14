from typing import Callable, Optional, Union, Dict

from typing import TypeVar
from requests.exceptions import InvalidURL

from kiota_abstractions.request_adapter import RequestAdapter
from kiota_http.httpx_request_adapter import HttpxRequestAdapter
from kiota_abstractions.method import Method
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.headers_collection import HeadersCollection
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization.parsable import Parsable
from kiota_serialization_json.json_serialization_writer import JsonSerializationWriter
from models import PageResult

T = TypeVar('T', bound=Parsable)


class PageIterator:

    def __init__(
        self,
        response: Union[T, list, object],
        request_adapter: HttpxRequestAdapter,
        constructor_callable: Optional[Callable] = None
    ):
        self.request_adapter = request_adapter

        if isinstance(response, Parsable) and not constructor_callable:
            constructor_callable = [type(response), 'create_from_discriminator_value']
        elif constructor_callable is None:
            constructor_callable = [PageResult, 'create_from_discriminator_value']
        self.constructor_callable = constructor_callable
        self.pause_index = 0
        self.headers: HeadersCollection = HeadersCollection()
        self.request_options = []  # check implementation of RequestOption and apply use it here
        self.current_page = self.convert_to_page(response)
        self.object_type = self.current_page.value[
            0].__class__.__name__ if self.current_page.value else None
        page = self.current_page

        if page is not None:
            self.current_page = page
            self.has_next = bool(page.odata_next_link)

    def set_headers(self, headers: dict) -> None:
        self.headers.update(**headers)

    def set_request_options(self, request_options: list) -> None:
        self.request_options = request_options

    def set_pause_index(self, pause_index: int) -> None:
        self.pause_index = pause_index

    async def iterate(self, callback: Callable) -> None:
        while True:
            keep_iterating = self.enumerate(callback)
            if not keep_iterating:
                return
            next_page = await self.next()
            print(f"Has next {next_page}")
            if not next_page:
                return
            self.current_page = next_page
            self.pause_index = 0

    async def next(self) -> Optional[dict]:
        if not self.current_page.odata_next_link:
            return None
        response = await self.fetch_next_page()
        return self.convert_to_page(response)

    @staticmethod
    def convert_to_page(response: Union[T, list, object]) -> PageResult:
        if not response:
            raise ValueError('Response cannot be null.')
        value = None
        if isinstance(response, list):
            value = response.value
        elif hasattr(response, 'value'):
            value = getattr(response, 'value')
        elif isinstance(response, object):
            value = getattr(response, 'value', [])
        if value is None:
            raise ValueError('The response does not contain a value.')
        parsable_page = response if isinstance(response, dict) else vars(response)
        next_link = parsable_page.get('odata_next_link', '') if isinstance(
            parsable_page, dict
        ) else getattr(parsable_page, 'odata_next_link', '')

        page = PageResult()
        page.odata_next_link = next_link
        page.set_value(value)
        return page

    async def fetch_next_page(self) -> dict:

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
        parsable_factory = PageResult(self.object_type)
        error_map = {}
        response = await self.request_adapter.send_async(request_info, parsable_factory, error_map)

        return response

    def enumerate(self, callback: Optional[Callable] = None) -> bool:
        keep_iterating = True
        page_items = self.current_page.value
        if not page_items:
            return False
        for i in range(self.pause_index, len(page_items)):
            keep_iterating = callback(page_items[i]) if callback is not None else True
            if not keep_iterating:
                self.pause_index = i + 1
                break
        return keep_iterating
