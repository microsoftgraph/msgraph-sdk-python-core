# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
#pylint: disable=undefined-variable
""" Demonstrate doing a batch request with a dependency on another request """

update_profile_pic_request = RequestInformation()
update_profile_pic_request.http_method = "PUT"
update_profile_pic_request.url = "/me/photo/$value"
update_profile_pic_request.headers = RequestHeaders()
update_profile_pic_request.headers.add("Content-Type", "image/jpeg")
current_directory = os.path.dirname(os.path.abspath(__file__))
image_file_path = os.path.join(current_directory, "my_cool_pic.jpeg")

with open(image_file_path, 'rb') as image_file:
    base64_image = base64.b64encode(image_file.read()).decode('ascii')

update_profile_pic_request.content = base64_image

# body has a bytes array
update_profile_photo_batch_item = BatchRequestItem(request_information=update_profile_pic_request)
print(f"batch with image {type(update_profile_photo_batch_item.body)}")

# Build the batch collection
batch_request_content_collection = BatchRequestContentCollection()
batch_request_content_collection.add_batch_request_item(update_profile_photo_batch_item)


async def get_batch_response():
    batch_response = await graph_client.batch.post(
        batch_request_content=batch_request_content_collection
    )
    for response_content in batch_response.get_responses():
        for request_id, response in response_content.responses.items():
            print(f"Batch response content collection {response.status}")
            print(f"Batch response content collection {response.body}")


asyncio.run(get_batch_response())
