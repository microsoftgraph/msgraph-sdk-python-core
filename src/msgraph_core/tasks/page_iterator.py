"""
This module contains the PageIterator class which is used to 
iterate over paged responses from a server.

The PageIterator class provides methods to iterate over the items 
in the pages, fetch the next page, convert a response to a page, and
 fetch the next page from the server.

The PageIterator class uses the Parsable interface to parse the responses
 from the server, the HttpxRequestAdapter class to send requests to the 
 server, and the PageResult class to represent the pages.

This module also imports the necessary types and exceptions from the 
typing, requests.exceptions, kiota_http.httpx_request_adapter,
 kiota_abstractions.method, kiota_abstractions.headers_collection, 
kiota_abstractions.request_information, kiota_abstractions.serialization.parsable,
and models modules.
"""

from typing import Callable, Optional, Union, Dict

from typing import TypeVar
from requests.exceptions import InvalidURL  # type: ignore

from kiota_http.httpx_request_adapter import HttpxRequestAdapter  # type: ignore
from kiota_abstractions.method import Method  # type: ignore
from kiota_abstractions.headers_collection import HeadersCollection  # type: ignore
from kiota_abstractions.request_information import RequestInformation  # type: ignore
from kiota_abstractions.serialization.parsable import Parsable  # type: ignore

# from models import PageResult  # pylint: disable=import-error
from msgraph_core.models.page_result import PageResult  # pylint: disable=import-error
# from ..models import PageResult  # pylint: disable=import-error

T = TypeVar('T', bound=Parsable)


class PageIterator:
    """
This class is used to iterate over paged responses from a server.

The PageIterator class provides methods to iterate over the items in the pages,
fetch the next page, and convert a response to a page.

Attributes:
    request_adapter (HttpxRequestAdapter): The adapter used to send HTTP requests.
    pause_index (int): The index at which to pause iteration.
    headers (HeadersCollection): The headers to include in the HTTP requests.
    request_options (list): The options for the HTTP requests.
    current_page (PageResult): The current page of items.
    object_type (str): The type of the items in the pages.
    has_next (bool): Whether there are more pages to fetch.

Methods:
    __init__(response: Union[T, list, object], request_adapter: HttpxRequestAdapter,
     constructor_callable: Optional[Callable] = None): Initializes a new instance of 
     the PageIterator class.
    """

    def __init__(
        self,
        response: Union[T, list, object],
        request_adapter: HttpxRequestAdapter,
        constructor_callable: Optional[Callable] = None
    ):
        self.request_adapter = request_adapter

        if isinstance(response, Parsable) and not constructor_callable:
            constructor_callable = getattr(type(response), 'create_from_discriminator_value')
        elif constructor_callable is None:
            constructor_callable = PageResult.create_from_discriminator_value
        self.pause_index = 0
        self.headers: HeadersCollection = HeadersCollection()
        self.request_options = []  # type: ignore
        self.current_page = self.convert_to_page(response)
        self.object_type = self.current_page.value[
            0].__class__.__name__ if self.current_page.value else None
        page = self.current_page

        if page is not None:
            self.current_page = page
            self.has_next = bool(page.odata_next_link)

    def set_headers(self, headers: dict) -> None:
        """
        Sets the headers for the HTTP requests.
        This method takes a dictionary of headers and adds them to the
        existing headers.
        Args:
            headers (dict): A dictionary of headers to add. The keys are the 
            header names and the values are the header values.
        """
        self.headers.add_all(**headers)

    def set_request_options(self, request_options: list) -> None:
        """
        Sets the request options for the HTTP requests.
        Args:
            request_options (list): The request options to set.
        """
        self.request_options = request_options

    def set_pause_index(self, pause_index: int) -> None:
        """
        Sets the index at which to pause iteration.
        Args:
            pause_index (int): The pause index to set.
        """
        self.pause_index = pause_index

    async def iterate(self, callback: Callable) -> None:
        """
        Iterates over the pages and applies a callback function to each item.
        The iteration stops when there are no more pages or the callback
         function returns False.
        Args:
            callback (Callable): The function to apply to each item. 
            It should take one argument (the item) and return a boolean.
        """
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
        """
        Fetches the next page of items.
        Returns:
            dict: The next page of items, or None if there are no more pages.
        """
        if not self.current_page.odata_next_link:
            return None
        response = await self.fetch_next_page()
        return self.convert_to_page(response)

    @staticmethod
    def convert_to_page(response: Union[T, list, object]) -> PageResult:
        """
        Converts a response to a PageResult.
        This method extracts the 'value' and 'odata_next_link' from the 
        response and uses them to create a PageResult.
        Args:
            response (Union[T, list, object]): The response to convert. It can
            be a list, an object, or any other type.
        Returns:
            PageResult: The PageResult created from the response.
        Raises:
            ValueError: If the response is None or does not contain a 'value'.
        """
        if not response:
            raise ValueError('Response cannot be null.')
        value = None
        if isinstance(response, list):
            value = response.value  # type: ignore
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
        """
        Fetches the next page of items from the server.
        Returns:
            dict: The response from the server.
        Raises:
            ValueError: If the current page does not contain a next link.
            InvalidURL: If the next link URL could not be parsed.
        """

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
        error_map: Dict[str, int] = {}
        response = await self.request_adapter.send_async(request_info, parsable_factory, error_map)

        return response

    def enumerate(self, callback: Optional[Callable] = None) -> bool:
        """
        Enumerates over the items in the current page and applies a
        callback function to each item.
        Args:
            callback (Callable, optional): The function to apply to each item.
            It should take one argument (the item) and return a boolean.
        Returns:
            bool: False if there are no items in the current page or the
            callback function returns False, True otherwise.
        """
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
