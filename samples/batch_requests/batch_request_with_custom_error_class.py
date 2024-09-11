# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
#pylint: disable=undefined-variable
"""Demonstrates using the Batch request with Custom Error Class"""

import asyncio

from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.serialization import Parsable
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.method import Method
from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders

from msgraph import GraphServiceClient

from msgraph_core.requests.batch_request_item import BatchRequestItem
from msgraph_core.requests.batch_request_content import BatchRequestContent

from msgraph_core.requests.batch_response_content import BatchResponseContent
from msgraph_core.requests.batch_request_builder import BatchRequestBuilder
# create client
# code to create client
user_client = GraphServiceClient(credentials=token, scopes=graph_scopes)


# Create an Error map Parsable or import it from wherever you have it
class CustomError(Parsable):

    def __init__(self) -> None:
        self.error_code: str = None
        self.message: str = None

    @staticmethod
    def not_found() -> 'CustomError':
        error = CustomError()
        error.error_code = "404"
        error.message = "Resource not found"
        return error


# Create a request adapter from client
request_adapter = user_client.request_adapter

# Create an instance of BatchRequestBuilder
batch_request_builder = BatchRequestBuilder(request_adapter)

# Create batch Items
request_info1 = RequestInformation()
request_info1.http_method = "GET"
request_info1.url = "https://graph.microsoft.com/v1.0/me"
request_info1.url = "/me"

request_info1.headers = RequestHeaders()
request_info1.headers.add("Content-Type", "application/json")

request_info2 = RequestInformation()
request_info2.http_method = "GET"
request_info2.url = "/users"
request_info2.headers = RequestHeaders()
request_info2.headers.add("Content-Type", "application/json")

# get user who does not exist to test 404 in error map
request_info3 = RequestInformation()
request_info3.http_method = "GET"
request_info3.url = "/users/random-id"
request_info3.headers = RequestHeaders()
request_info3.headers.add("Content-Type", "application/json")

# bacth request items to be added to content
batch_request_item1 = BatchRequestItem(request_information=request_info1)
batch_request_item2 = BatchRequestItem(request_information=request_info2)
batch_request_item3 = BatchRequestItem(request_information=request_info3)

# Create a BatchRequestContent
batch_request_content = [batch_request_item1, batch_request_item2, batch_request_item3]
batch_content = BatchRequestContent(batch_request_content)


# Function to demonstrate the usage of BatchRequestBuilder
async def main():
    error_map = {"400": CustomError, "404": CustomError.not_found}

    batch_response_content = await batch_request_builder.post(
        batch_request_content=batch_content, error_map=error_map
    )

    # Print the batch response content
    print(f"Batch Response Content: {batch_response_content.responses}")
    for response in batch_response_content.responses:
        print(f"Request ID: {response.id}, Status: {response.status}")
        print(f"Response body: {response.body}, headers: {response.headers}")
        print("-------------------------------------------------------------")


asyncio.run(main())
