from typing import TypeVar, Dict
import json

from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.method import Method
from kiota_abstractions.serialization import Parsable
from kiota_abstractions.headers_collection import HeadersCollection
from kiota_abstractions.api_error import APIError

from .batch_request_content import BatchRequestContent
from .batch_response_content import BatchResponseContent

T = TypeVar('T', bound='Parsable')


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
    ) -> BatchResponseContent:
        """
        Sends a batch request and returns the batch response content.
        
        Args:
            batch_request_content (BatchRequestContent): The batch request content.
            error_map (Optional[Dict[str, ParsableFactory[Parsable]]]): 
                Error mappings for response handling.

        Returns:
            BatchResponseContent: The batch response content.
        """
        if batch_request_content is None:
            raise ValueError("batch_request_content cannot be Null.")
        request_info = await self.to_post_request_information(batch_request_content)
        content = json.loads(request_info.content.decode("utf-8"))
        json_body = json.dumps(content)
        request_info.content = json_body
        error_map: Dict[str, int] = {}
        response = None
        try:
            response = await self._request_adapter.send_async(
                request_info, BatchResponseContent, error_map
            )
        except APIError as e:
            print(f"API Error: {e}")
        if response is None:
            raise ValueError("Failed to get a valid response from the API.")
        print(f"Response before processing: {response}")
        return response

    async def to_post_request_information(
        self,
        batch_request_content: BatchRequestContent,
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
        requests_dict = [item.get_field_deserializers() for item in batch_request_content.requests]
        request_info.content = json.dumps({"requests": requests_dict}).encode("utf-8")

        request_info.headers = HeadersCollection()
        request_info.headers.try_add("Content-Type", "application/json")
        request_info.set_content_from_parsable(
            self._request_adapter, "application/json", batch_request_content
        )

        return request_info
