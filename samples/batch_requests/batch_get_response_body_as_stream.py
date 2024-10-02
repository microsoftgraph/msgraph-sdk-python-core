# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
#pylint: disable=undefined-variable
""" Demonstrate getting response body as stream in Batch Responses"""
batch_request_content = {
    batch_request_item1.id: batch_request_item1,
    batch_request_item2.id: batch_request_item2
}

batch_content = BatchRequestContent(batch_request_content)


async def main():
    batch_response_content = await client.batch.post(batch_request_content=batch_content)

    try:
        stream_response = batch_response_content.get_response_stream_by_id(batch_request_item1.id)
        print(f"Stream Response: {stream_response}")
        print(f"Stream Response Content: {stream_response.read()}")
    except AttributeError as e:
        print(f"Error getting response by ID: {e}")


asyncio.run(main())
