import logging
from typing import Optional, Type, TypeVar, Union

from kiota_abstractions.api_error import APIError
from kiota_abstractions.headers_collection import HeadersCollection
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import Parsable, ParsableFactory

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
        error_map: Optional[dict[str, Type[ParsableFactory]]] = None
    ):
        if request_adapter is None:
            raise ValueError("request_adapter cannot be Null.")
        self._request_adapter = request_adapter
        self.url_template = f"{self._request_adapter.base_url.removesuffix('/')}/$batch"
        self.error_map = error_map or {}

    async def post(
        self,
        batch_request_content: Union[BatchRequestContent, BatchRequestContentCollection],
        error_map: Optional[dict[str, Type[ParsableFactory]]] = None,
    ) -> Union[BatchResponseContent, BatchResponseContentCollection]:
        """
        Sends a batch request and returns the batch response content.

        Args:
            batch_request_content (Union[BatchRequestContent,
            BatchRequestContentCollection]): The batch request content.
            Optional[dict[str, Type[ParsableFactory]]] = None:
                Error mappings for response handling.

        Returns:
            Union[BatchResponseContent, BatchResponseContentCollection]: The batch response content
             or the specified response type.

        """
        if batch_request_content is None:
            raise ValueError("batch_request_content cannot be Null.")
        response_type = BatchResponseContent

        if isinstance(batch_request_content, BatchRequestContent):
            request_info = await self.to_post_request_information(batch_request_content)
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
        error_map: Optional[dict[str, Type[ParsableFactory]]] = None,
    ) -> BatchResponseContentCollection:
        """
        Sends a collection of batch requests and returns a collection of batch response contents.

        Args:
            batch_request_content_collection (BatchRequestContentCollection): The
            collection of batch request contents.
            Optional[dict[str, Type[ParsableFactory]]] = None:
                Error mappings for response handling.

        Returns:
            BatchResponseContentCollection: The collection of batch response contents.
        """
        if batch_request_content_collection is None:
            raise ValueError("batch_request_content_collection cannot be Null.")

        batch_responses = BatchResponseContentCollection()
        batch_requests = batch_request_content_collection.get_batch_requests_for_execution()
        for batch_request_content in batch_requests:
            response = await self.post(batch_request_content, error_map)
            if isinstance(response, BatchResponseContent):
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

        request_info = RequestInformation()
        request_info.http_method = Method.POST
        request_info.url_template = self.url_template
        request_info.headers = HeadersCollection()
        request_info.headers.try_add("Content-Type", APPLICATION_JSON)
        request_info.set_content_from_parsable(
            self._request_adapter, APPLICATION_JSON, batch_request_content
        )

        return request_info
