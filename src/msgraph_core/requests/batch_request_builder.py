from typing import TypeVar, Type, Dict, Optional, Union
import logging

from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.method import Method
from kiota_abstractions.serialization import Parsable
from kiota_abstractions.headers_collection import HeadersCollection
from kiota_abstractions.api_error import APIError

from .batch_request_content import BatchRequestContent
from .batch_request_content_collection import BatchRequestContentCollection
from .batch_response_content import BatchResponseContent
from .batch_response_content_collection import BatchResponseContentCollection

T = TypeVar('T', bound='Parsable')

APPLICATION_JSON = "application/json"


class BatchRequestBuilder:
    """
    Provides operations to call the batch method.
    """

    def __init__(
        self,
        request_adapter: RequestAdapter,
        error_map: Optional[Dict[str, Type[Parsable]]] = None
    ):
        if request_adapter is None:
            raise ValueError("request_adapter cannot be Null.")
        self._request_adapter = request_adapter
        self.url_template = f"{self._request_adapter.base_url}/$batch"
        self.error_map = error_map or {}

    async def post(
        self,
        batch_request_content: Union[BatchRequestContent, BatchRequestContentCollection],
        error_map: Optional[Dict[str, Type[Parsable]]] = None,
    ) -> Union[T, BatchResponseContentCollection]:
        """
        Sends a batch request and returns the batch response content.
        
        Args:
            batch_request_content (Union[BatchRequestContent, 
            BatchRequestContentCollection]): The batch request content.
            response_type: Optional[Type[T]] : The type to deserialize the response into.
            Optional[Dict[str, Type[Parsable]]] = None: 
                Error mappings for response handling.

        Returns:
            Union[T, BatchResponseContentCollection]: The batch response content
             or the specified response type.

        """
        if batch_request_content is None:
            raise ValueError("batch_request_content cannot be Null.")
        response_type = BatchResponseContent

        if isinstance(batch_request_content, BatchRequestContent):
            request_info = await self.to_post_request_information(batch_request_content)
            bytes_content = request_info.content
            json_content = bytes_content.decode("utf-8")
            updated_str = '{"requests":' + json_content + '}'
            updated_bytes = updated_str.encode("utf-8")
            request_info.content = updated_bytes
            error_map = error_map or self.error_map
            response = None
            try:
                response = await self._request_adapter.send_async(
                    request_info, response_type, error_map
                )

            except APIError as e:
                logging.error("API Error: %s", e)
                raise e
            if response is None:
                raise ValueError("Failed to get a valid response from the API.")
            return response
        if isinstance(batch_request_content, BatchRequestContentCollection):
            batch_responses = await self._post_batch_collection(batch_request_content, error_map)
            return batch_responses

        raise ValueError("Invalid type for batch_request_content.")

    async def _post_batch_collection(
        self,
        batch_request_content_collection: BatchRequestContentCollection,
        error_map: Optional[Dict[str, Type[Parsable]]] = None,
    ) -> BatchResponseContentCollection:
        """
        Sends a collection of batch requests and returns a collection of batch response contents.
        
        Args:
            batch_request_content_collection (BatchRequestContentCollection): The 
            collection of batch request contents.
            Optional[Dict[str, Type[Parsable]]] = None: 
                Error mappings for response handling.

        Returns:
            BatchResponseContentCollection: The collection of batch response contents.
        """
        if batch_request_content_collection is None:
            raise ValueError("batch_request_content_collection cannot be Null.")

        batch_responses = BatchResponseContentCollection()

        for batch_request_content in batch_request_content_collection.batches:
            request_info = await self.to_post_request_information(batch_request_content)
            response = await self._request_adapter.send_async(
                request_info, BatchResponseContent, error_map or self.error_map
            )
            batch_responses.add_response(response)

        return batch_responses

    async def to_post_request_information(
        self, batch_request_content: BatchRequestContent
    ) -> RequestInformation:
        """
        Creates request information for a batch POST request.
        
        Args:
            batch_request_content (BatchRequestContent): The batch request content.

        Returns:
            RequestInformation: The request information.
        """

        if batch_request_content is None:
            raise ValueError("batch_request_content cannot be Null.")
        batch_request_items = list(batch_request_content.requests.values())

        request_info = RequestInformation()
        request_info.http_method = Method.POST
        request_info.url_template = self.url_template
        request_info.headers = HeadersCollection()
        request_info.headers.try_add("Content-Type", APPLICATION_JSON)
        request_info.set_content_from_parsable(
            self._request_adapter, APPLICATION_JSON, batch_request_items
        )

        return request_info
