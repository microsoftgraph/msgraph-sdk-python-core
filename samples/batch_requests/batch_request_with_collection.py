# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
#pylint: disable=undefined-variable
"""Demonstrates using the Batch request with Collection"""
import asyncio

from urllib.request import Request
from kiota_abstractions.request_information import RequestInformation

from msgraph import GraphServiceClient

from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders
from msgraph_core.requests.batch_request_item import BatchRequestItem

from msgraph_core.requests.batch_request_content import BatchRequestContent
from msgraph_core.requests.batch_request_content_collection import BatchRequestContentCollection
# Create a client
# code to create graph client

graph_client = GraphServiceClient(credentials=token, scopes=graph_scopes)

# Create a request adapter from the client
request_adapter = graph_client.request_adapter

# Create some BatchRequestItems

request_info1 = RequestInformation()
request_info1.http_method = "GET"
request_info1.url = "/me"
request_info1.headers = RequestHeaders()
request_info1.headers.add("Content-Type", "application/json")

request_info2 = RequestInformation()
request_info2.http_method = "GET"
request_info2.url = "/users"
request_info2.headers = RequestHeaders()
request_info2.headers.add("Content-Type", "application/json")

request_info3 = RequestInformation()
request_info3.http_method = "GET"
request_info3.url = "/me"
request_info3.headers = RequestHeaders()
request_info3.headers.add("Content-Type", "application/json")

# Create BatchRequestItem instances
batch_request_item1 = BatchRequestItem(request_information=request_info1)
batch_request_item2 = BatchRequestItem(request_information=request_info2)

# Add a request using RequestInformation directly
batch_request_content.add_request_information(request_info1)
print(
    f"Number of requests after adding request using RequestInformation: {len(batch_request_content.requests)}"
)
print("------------------------------------------------------------------------------------")
# Create an instance of BatchRequestContentCollection
collection = BatchRequestContentCollection()
# Add request items to the collection
batch_request_item_to_add = BatchRequestItem(request_information=request_info3)
batch_request_item_to_add1 = BatchRequestItem(request_information=request_info3)
batch_request_item_to_add2 = BatchRequestItem(request_information=request_info3)
batch_request_item_to_add3 = BatchRequestItem(request_information=request_info3)
batch_request_item_to_add4 = BatchRequestItem(request_information=request_info3)

collection.add_batch_request_item(batch_request_item_to_add)
collection.add_batch_request_item(batch_request_item_to_add1)
collection.add_batch_request_item(batch_request_item_to_add2)
collection.add_batch_request_item(batch_request_item_to_add3)
collection.add_batch_request_item(batch_request_item_to_add4)

# Print the current batch requests
print("Current Batch Requests:")
for request in collection.current_batch.requests:
    print(f"Request ID: {request.id}, Status Code: {request.headers}")

# Remove a request item from the collection
collection.remove_batch_request_item(batch_request_item_to_add.id)
print(f"Items left in the batch after removal: {len(collection.current_batch.requests)}")


# post a collection
async def main():

    batch_response_content = await graph_client.batch.post(batch_request_content=collection)
    responses = batch_response_content.get_responses()
    for item in responses:
        for item_body in item.responses:
            print(f"Item: {item_body.id}, Status Code: {item_body.status}")
            print(f"body: {item_body.body} Item headers: {item_body.headers} ")
            print("-----------------------------------------------")


# Run the main function
asyncio.run(main())
