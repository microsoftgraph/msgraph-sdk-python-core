import pytest
import json
from io import BytesIO
from unittest.mock import Mock
from urllib.request import Request
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization.serialization_writer import SerializationWriter
from kiota_abstractions.method import Method
from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders
from kiota_serialization_json.json_serialization_writer_factory import JsonSerializationWriterFactory
from msgraph_core.requests.batch_request_item import BatchRequestItem

base_url = "https://graph.microsoft.com/v1.0/me"


@pytest.fixture
def request_info():
    request_info = RequestInformation() 
    request_info.http_method = "GET"
    request_info.url = base_url
    request_info.headers = RequestHeaders()
    request_info.headers.add("Content-Type", "application/json")
    request_info.content = b'{"key": "value"}'
    return request_info


@pytest.fixture
def batch_request_item(request_info):
    return BatchRequestItem(request_information=request_info, id="123")


def test_initialization(batch_request_item, request_info):
    assert batch_request_item.id == "123"
    assert batch_request_item.method == "GET"
    assert batch_request_item.url == base_url
    assert batch_request_item.headers == {"content-type": "application/json"}
    assert batch_request_item.body == b'{"key": "value"}'


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
    assert batch_request_item.headers["authorization"] == "Bearer token"


def test_body_property(batch_request_item):
    new_body = BytesIO(b'{"new_key": "new_value"}')
    batch_request_item.body = new_body
    assert batch_request_item.body == b'{"new_key": "new_value"}'


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


def test_serialize_json(batch_request_item):
    writer = JsonSerializationWriterFactory().get_serialization_writer('application/json')
    batch_request_item.serialize(writer)
    content = json.loads(writer.get_serialized_content())
    assert content["id"] == "123"
    assert content["method"] == "GET"
    assert content["url"] == base_url
    assert content["headers"] == {"content-type": "application/json"}
    assert content["body"] == {"key": "value"}

