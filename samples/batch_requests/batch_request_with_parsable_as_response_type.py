# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
#pylint: disable=undefined-variable
"""Demonstrates using the Batch request with Parsable Resposnse Type"""
import asyncio

from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.method import Method
from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders

from msgraph_core.requests.batch_request_item import BatchRequestItem
from msgraph_core.requests.batch_request_content import BatchRequestContent

# import User model to serialize to
from msgraph.generated.models.user import User
# Create a client
# code to create graph client
graph_client = GraphServiceClient(credentials=token, scopes=graph_scopes)

print(f"Graph Scopes: {graph_scopes}")

# Create a  request adapter from the client
request_adapter = graph_client.request_adapter

# Create batch Items
request_info1 = RequestInformation()
request_info1.http_method = "GET"
request_info1.url = "/users/<user-id-1>"

request_info1.headers = RequestHeaders()
request_info1.headers.add("Content-Type", "application/json")

request_info2 = RequestInformation()
request_info2.http_method = "GET"
request_info2.url = "/users/<user-id-2>"
request_info2.headers = RequestHeaders()
request_info2.headers.add("Content-Type", "application/json")

# bacth request items to be added to content
batch_request_item1 = BatchRequestItem(request_information=request_info1)
batch_request_item2 = BatchRequestItem(request_information=request_info2)

# Create a batch request content
batch_request_content = {
    batch_request_item1.id: batch_request_item1,
    batch_request_item2.id: batch_request_item2
}

batch_content = BatchRequestContent(batch_request_content)


# Function to demonstrate the usage of BatchRequestBuilder
async def main():
    batch_response_content = await graph_client.batch.post(batch_request_content=batch_content)
    # response_type=User

    try:
        individual_response = batch_response_content.get_response_by_id(
            batch_request_item1.id, User
        )
        print(f"Individual Response: {individual_response}")
    except AttributeError as e:
        print(f"Error getting response by ID: {e}")


asyncio.run(main())
