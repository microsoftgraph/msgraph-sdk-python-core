import pytest
from unittest.mock import Mock
from urllib.request import Request
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.serialization import SerializationWriter
from msgraph_core.requests.batch_request_item import BatchRequestItem
from msgraph_core.requests.batch_request_content import BatchRequestContent
from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders
from msgraph_core.requests.batch_request_item import BatchRequestItem, StreamInterface


@pytest.fixture
def request_info1():
    request_info = RequestInformation()
    request_info.http_method = "GET"
    request_info.url = "https://graph.microsoft.com/v1.0/me"
    request_info.headers = RequestHeaders()
    request_info.headers.add("Content-Type", "application/json")
    request_info.content = StreamInterface(b'{"key": "value"}')
    return request_info


@pytest.fixture
def request_info2():
    request_info = RequestInformation()
    request_info.http_method = "POST"
    request_info.url = "https://graph.microsoft.com/v1.0/users"
    request_info.headers = RequestHeaders()
    request_info.headers.add("Content-Type", "application/json")
    request_info.content = StreamInterface(b'{"key": "value"}')
    return request_info


@pytest.fixture
def batch_request_item1(request_info1):
    return BatchRequestItem(request_information=request_info1)


@pytest.fixture
def batch_request_item2(request_info2):
    return BatchRequestItem(request_information=request_info2)


@pytest.fixture
def batch_request_content(batch_request_item1, batch_request_item2):
    return BatchRequestContent(
        {
            batch_request_item1.id: batch_request_item1,
            batch_request_item2.id: batch_request_item2
        }
    )


def test_initialization(batch_request_content, batch_request_item1, batch_request_item2):
    assert len(batch_request_content.requests) == 2


def test_requests_property(batch_request_content, batch_request_item1, batch_request_item2):
    new_request_item = batch_request_item1
    batch_request_content.requests = [batch_request_item1, batch_request_item2, new_request_item]
    assert len(batch_request_content.requests) == 2
    assert batch_request_content.requests[batch_request_item1.id] == new_request_item


def test_add_request(batch_request_content, batch_request_item1):
    new_request_item = request_info1
    new_request_item.id = "new_id"
    batch_request_content.add_request(new_request_item.id, new_request_item)
    assert len(batch_request_content.requests) == 3
    assert batch_request_content.requests[new_request_item.id] == new_request_item


def test_add_request_information(batch_request_content):
    new_request_info = RequestInformation()
    new_request_info.http_method = "DELETE"
    new_request_info.url = "https://graph.microsoft.com/v1.0/groups"
    batch_request_content.add_request_information(new_request_info)
    assert len(batch_request_content.requests) == 3


def test_add_urllib_request(batch_request_content):
    urllib_request = Request("https://graph.microsoft.com/v1.0/me", method="PATCH")
    urllib_request.add_header("Content-Type", "application/json")
    urllib_request.data = b'{"key": "value"}'
    batch_request_content.add_urllib_request(urllib_request)
    assert len(batch_request_content.requests) == 3


def test_finalize(batch_request_content):
    finalized_requests = batch_request_content.finalize()
    assert batch_request_content.is_finalized
    assert finalized_requests == batch_request_content.requests


def test_create_from_discriminator_value():
    parse_node = Mock()
    batch_request_content = BatchRequestContent.create_from_discriminator_value(parse_node)
    assert isinstance(batch_request_content, BatchRequestContent)


def test_get_field_deserializers(batch_request_content):
    deserializers = batch_request_content.get_field_deserializers()
    assert isinstance(deserializers, dict)


def test_serialize(batch_request_content):
    writer = Mock(spec=SerializationWriter)
    batch_request_content.serialize(writer)
    writer.write_collection_of_object_values.assert_called_once_with(
        "requests", batch_request_content.requests
    )
