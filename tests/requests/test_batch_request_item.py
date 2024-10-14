import pytest
from unittest.mock import Mock
import base64
import json

from urllib.request import Request
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.method import Method
from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders
from msgraph_core.requests.batch_request_item import BatchRequestItem, StreamInterface
from kiota_abstractions.serialization import SerializationWriter

base_url = "https://graph.microsoft.com/v1.0/me"


@pytest.fixture
def request_info():
    request_info = RequestInformation()
    request_info.http_method = "GET"
    request_info.url = "f{base_url}/me"
    request_info.headers = RequestHeaders()
    request_info.content = StreamInterface(b'{"key": "value"}')
    return request_info


@pytest.fixture
def batch_request_item(request_info):
    return BatchRequestItem(request_information=request_info)


@pytest.fixture
def request_info_json():
    request_info = RequestInformation()
    request_info.http_method = "POST"
    request_info.url = "https://graph.microsoft.com/v1.0/me/events"
    request_info.headers = RequestHeaders()
    request_info.headers.add("Content-Type", "application/json")
    request_info.content = json.dumps(
        {
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
    ).encode('utf-8')
    return request_info


@pytest.fixture
def request_info_bytes():
    request_info = RequestInformation()
    request_info.http_method = "POST"
    request_info.url = "https://graph.microsoft.com/v1.0/me/events"
    request_info.headers = RequestHeaders()
    request_info.headers.add("Content-Type", "application/json")
    request_info.content = b'{"@odata.type": "#microsoft.graph.event", "end": {"dateTime": "2024-10-14T17:30:00", "timeZone": "Pacific Standard Time"}, "start": {"dateTime": "2024-10-14T17:00:00", "timeZone": "Pacific Standard Time"}, "subject": "File end-of-day report"}'
    return request_info


@pytest.fixture
def batch_request_item_json(request_info_json):
    return BatchRequestItem(request_information=request_info_json)


@pytest.fixture
def batch_request_item_bytes(request_info_bytes):
    return BatchRequestItem(request_information=request_info_bytes)


def test_initialization(batch_request_item, request_info):
    assert batch_request_item.method == "GET"
    assert batch_request_item.url == "f{base_url}/me"
    assert batch_request_item.body.read() == b'{"key": "value"}'


def test_create_with_urllib_request():
    urllib_request = Request("https://graph.microsoft.com/v1.0/me", method="POST")
    urllib_request.add_header("Content-Type", "application/json")
    urllib_request.data = b'{"key": "value"}'
    batch_request_item = BatchRequestItem.create_with_urllib_request(urllib_request)
    assert batch_request_item.method == "POST"
    assert batch_request_item.url == "https://graph.microsoft.com/v1.0/me"
    assert batch_request_item.body == b'{"key": "value"}'


def test_set_depends_on(batch_request_item):
    batch_request_item.set_depends_on(["request1", "request2"])
    assert batch_request_item.depends_on == ["request1", "request2"]


def test_set_url(batch_request_item):
    batch_request_item.set_url("https://graph.microsoft.com/v1.0/me")
    assert batch_request_item.url == "/v1.0/me"


def test_constructor_url_replacement():
    request_info = RequestInformation()
    request_info.http_method = "GET"
    request_info.url = "https://graph.microsoft.com/v1.0/users/me-token-to-replace"
    request_info.headers = RequestHeaders()
    request_info.content = None

    batch_request_item = BatchRequestItem(request_info)

    assert batch_request_item.url == "https://graph.microsoft.com/v1.0/me"


def test_set_url_replacement():
    request_info = RequestInformation()
    request_info.http_method = "GET"
    request_info.url = "https://graph.microsoft.com/v1.0/users/me-token-to-replace"
    request_info.headers = RequestHeaders()
    request_info.content = None

    batch_request_item = BatchRequestItem(request_info)
    batch_request_item.set_url("https://graph.microsoft.com/v1.0/users/me-token-to-replace")

    assert batch_request_item.url == "/v1.0/me"


def test_constructor_url_replacement_with_query():
    request_info = RequestInformation()
    request_info.http_method = "GET"
    request_info.url = "https://graph.microsoft.com/v1.0/users/me-token-to-replace?param=value"
    request_info.headers = RequestHeaders()
    request_info.content = None

    batch_request_item = BatchRequestItem(request_info)

    assert batch_request_item.url == "https://graph.microsoft.com/v1.0/me?param=value"


def test_id_property(batch_request_item):
    batch_request_item.id = "new_id"
    assert batch_request_item.id == "new_id"


def test_headers_property(batch_request_item):
    new_headers = {"Authorization": "Bearer token"}
    batch_request_item.headers = new_headers
    assert batch_request_item.headers["Authorization"] == "Bearer token"


def test_body_property(batch_request_item):
    new_body = StreamInterface(b'{"new_key": "new_value"}')
    batch_request_item.body = new_body
    assert batch_request_item.body.read() == b'{"new_key": "new_value"}'


def test_method_property(batch_request_item):
    batch_request_item.method = "POST"
    assert batch_request_item.method == "POST"


def test_batch_request_item_method_enum():
    # Create a RequestInformation instance with an enum value for http_method
    request_info = RequestInformation()
    request_info.http_method = Method.GET
    request_info.url = "https://graph.microsoft.com/v1.0/me"
    request_info.headers = RequestHeaders()
    request_info.content = None
    batch_request_item = BatchRequestItem(request_information=request_info)
    assert batch_request_item.method == "GET"


def test_depends_on_property(batch_request_item):
    batch_request_item.set_depends_on(["request1", "request2"])
    assert batch_request_item.depends_on == ["request1", "request2"]


def test_serialize_with_json_body(batch_request_item_json):
    writer = Mock(spec=SerializationWriter)

    batch_request_item_json.serialize(writer)

    writer.write_str_value.assert_any_call('id', batch_request_item_json.id)
    writer.write_str_value.assert_any_call('method', batch_request_item_json.method)
    writer.write_str_value.assert_any_call('url', batch_request_item_json.url)
    writer.write_collection_of_primitive_values.assert_any_call(
        'depends_on', batch_request_item_json.depends_on
    )

    writer.write_str_value.assert_any_call('body', batch_request_item_json._body.decode('utf-8'))


def test_serialize_with_bytes_body(batch_request_item_bytes):
    writer = Mock(spec=SerializationWriter)

    batch_request_item_bytes.serialize(writer)

    writer.write_str_value.assert_any_call('id', batch_request_item_bytes.id)
    writer.write_str_value.assert_any_call('method', batch_request_item_bytes.method)
    writer.write_str_value.assert_any_call('url', batch_request_item_bytes.url)
    writer.write_collection_of_primitive_values.assert_any_call(
        'depends_on', batch_request_item_bytes.depends_on
    )

    writer.write_str_value.assert_any_call('body', batch_request_item_bytes._body.decode('utf-8'))
