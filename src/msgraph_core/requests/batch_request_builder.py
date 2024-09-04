from typing import Dict, Optional, List
import asyncio
import json

from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.serialization import ParsableFactory
from kiota_abstractions.serialization import Parsable
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.method import Method
from kiota_abstractions.headers_collection import HeadersCollection

from .batch_request_content import BatchRequestContent
from .batch_request_content_collection import BatchRequestContentCollection
from .batch_response_content import BatchResponseContent
from .batch_response_content_collection import BatchResponseContentCollection


class BatchRequestBuilder:
    """
    Provides operations to call the batch method.
    """

    def __init__(self, request_adapter: RequestAdapter):
        if request_adapter is None:
            raise ValueError("request_adapter cannot be Null.")
        self._request_adapter = request_adapter
        self.url_template = "{}/$batch".format(self._request_adapter.base_url)

    async def post_content(
        self,
        batch_request_content: BatchRequestContent,
        # error_map: Dict[str, int] = {}
    ) -> BatchResponseContent:
        """
        Sends a batch request and returns the batch response content.
        
        Args:
            batch_request_content (BatchRequestContent): The batch request content.
            error_map (Optional[Dict[str, ParsableFactory[Parsable]]]): Error mappings for response handling.

        Returns:
            BatchResponseContent: The batch response content.
        """
        if batch_request_content is None:
            raise ValueError("batch_request_content cannot be Null.")
        request_info = await self.to_post_request_information(batch_request_content)
        # print(f"Request Info: {request_info}")
        print(f"Request Info Content: {request_info.content}")
        # print(f"Request Info Headers: {request_info.headers}")
        # print(f"Request Info Method: {request_info.http_method}")
        # print(f"Request Info URL: {request_info.url}")
        # could we use a native response handler here?
        parsable_factory = BatchResponseContent()
        error_map: Dict[str, int] = {}
        response = await self._request_adapter.send_async(request_info, parsable_factory, error_map)
        return response

    async def to_post_request_information(
        self,
        batch_request_content: 'BatchRequestContent',
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
        # serialized_content = [
        #     item.get_field_deserializers() for item in batch_request_content.requests
        # ]
        # print(f"Serialized Content: {type(serialized_content)}")
        # request_info.content = json.dumps(serialized_content).encode("utf-8")
        request_info.headers = HeadersCollection()
        request_info.headers.try_add("Content-Type", "application/json")
        return request_info
