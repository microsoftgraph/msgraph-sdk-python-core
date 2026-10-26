# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
#pylint: disable=undefined-variable
""" Demonstrate doing a batch request with binary content """
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

# set query parameters for the calendar view
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

events_batch_item = BatchRequestItem(
    request_information=events_request, depends_on=[add_event_batch_item]
)

# Build the batch collection
batch_request_content_collection = BatchRequestContentCollection()
batch_request_content_collection.add_batch_request_item(add_event_batch_item)
batch_request_content_collection.add_batch_request_item(events_batch_item)


async def get_batch_response():
    batch_response = await graph_client.batch.post(
        batch_request_content=batch_request_content_collection
    )
    for response_content in batch_response.get_responses():
        for request_id, response in response_content.responses.items():
            print(f"Batch response content collection {response.status}")
            print(f"Batch response content collection {response.body}")


asyncio.run(get_batch_response())
