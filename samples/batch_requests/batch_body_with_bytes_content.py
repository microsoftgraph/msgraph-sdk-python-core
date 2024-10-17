# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
#pylint: disable=undefined-variable
""" Demonstrate doing a batch request with a dependency on another request """

graph_client = GraphServiceClient(credentials=token, scopes=graph_scopes)
# Use the request builder to generate a regular
# request to /me
user_request = graph_client.me.to_get_request_information()

today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
tomorrow = today + timedelta(days=1)

new_event = Event(
    subject="File end-of-day report",
    start=DateTimeTimeZone(
        date_time=(today + timedelta(hours=17)).isoformat(timespec='seconds'),
        time_zone='Pacific Standard Time'
    ),
    end=DateTimeTimeZone(
        date_time=(today + timedelta(hours=17, minutes=30)).isoformat(timespec='seconds'),
        time_zone='Pacific Standard Time'
    )
)

# Use the request builder to generate a regular
add_event_request = graph_client.me.events.to_post_request_information(new_event)

# Use the request builder to generate a regular
# request to /me/calendarview?startDateTime="start"&endDateTime="end"
query_params = CalendarViewRequestBuilder.CalendarViewRequestBuilderGetQueryParameters(
    start_date_time=today.isoformat(timespec='seconds'),
    end_date_time=tomorrow.isoformat(timespec='seconds')
)

config = CalendarViewRequestBuilder.CalendarViewRequestBuilderGetRequestConfiguration(
    query_parameters=query_params
)
events_request = graph_client.me.calendar_view.to_get_request_information(config)

# Build the batch
add_event_batch_item = BatchRequestItem(request_information=add_event_request)
add_event_batch_item.body = {
    "@odata.type": "#microsoft.graph.event",
    "end": {
        "dateTime": "2024-10-14T17:30:00",
        "timeZone": "Pacific Standard Time"
    },
    "start": {
        "dateTime": "2024-10-14T17:00:00",
        "timeZone": "Pacific Standard Time"
    },
    "subject": "File end-of-day report"
}
add_event_batch_item.body = json.dumps(add_event_batch_item.body)

print(f"Event to be added {type(add_event_batch_item.body)}")

events_batch_item = BatchRequestItem(request_information=events_request)

update_profile_pic_request = RequestInformation()
update_profile_pic_request.http_method = "PUT"
update_profile_pic_request.url = "/me/photo/$value"
update_profile_pic_request.headers = RequestHeaders()
update_profile_pic_request.headers.add("Content-Type", "image/jpeg")
current_directory = os.path.dirname(os.path.abspath(__file__))
image_file_path = os.path.join(current_directory, "app_headshot.jpeg")

with open(image_file_path, 'rb') as image_file:
    # base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    base64_image = base64.b64encode(image_file.read()).decode('ascii')

update_profile_pic_request.content = base64_image
# output_file_path = os.path.join(current_directory, "app_image_bytes.txt")

print(f"Image content {type(update_profile_pic_request.content)}")
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
