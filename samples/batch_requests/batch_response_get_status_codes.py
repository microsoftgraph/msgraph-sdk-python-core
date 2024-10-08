# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
#pylint: disable=undefined-variable
"""Demonstrates getting status codes in Batch Responses"""
batch_request_content = {
    batch_request_item1.id: batch_request_item1,
    batch_request_item2.id: batch_request_item2
}

batch_content = BatchRequestContent(batch_request_content)


async def main():
    batch_response_content = await client.batch.post(batch_request_content=batch_content)

    try:
        status_codes = batch_response_content.get_response_status_codes()
        print(f"Status Codes: {status_codes}")
    except AttributeError as e:
        print(f"Error getting respons status codes: {e}")


asyncio.run(main())
