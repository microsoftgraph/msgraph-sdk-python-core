import pytest
from io import BytesIO

from kiota_abstractions.serialization import ParseNode, SerializationWriter
from unittest.mock import Mock

from msgraph_core.requests.batch_response_item import BatchResponseItem


@pytest.fixture
def batch_response_item():
    return BatchResponseItem()


def test_initialization(batch_response_item):
    assert batch_response_item.id is None
    assert batch_response_item.atomicity_group is None
    assert batch_response_item.status is None
    assert batch_response_item.headers == {}
    assert batch_response_item.body is None


def test_id_property(batch_response_item):
    batch_response_item.id = "12345"
    assert batch_response_item.id == "12345"


def test_atomicity_group_property(batch_response_item):
    batch_response_item.atomicity_group = "group1"
    assert batch_response_item.atomicity_group == "group1"


def test_status_property(batch_response_item):
    batch_response_item.status = 200
    assert batch_response_item.status == 200


def test_headers_property(batch_response_item):
    headers = {"Content-Type": "application/json"}
    batch_response_item.headers = headers
    assert batch_response_item.headers == headers


def test_body_property(batch_response_item):
    body = BytesIO(b"response body")
    batch_response_item.body = body
    assert batch_response_item.body == body


def test_content_type_property(batch_response_item):
    headers = {"Content-Type": "application/json"}
    batch_response_item.headers = headers
    assert batch_response_item.content_type == "application/json"


def test_create_from_discriminator_value():
    parse_node = Mock(spec=ParseNode)
    batch_response_item = BatchResponseItem.create_from_discriminator_value(parse_node)
    assert isinstance(batch_response_item, BatchResponseItem)


def test_get_field_deserializers(batch_response_item):
    deserializers = batch_response_item.get_field_deserializers()
    assert isinstance(deserializers, dict)
    assert "id" in deserializers
    assert "status" in deserializers
    assert "headers" in deserializers
    assert "body" in deserializers


def test_serialize(batch_response_item):
    writer = Mock(spec=SerializationWriter)
    batch_response_item.id = "12345"
    batch_response_item.atomicity_group = "group1"
    batch_response_item.status = 200
    batch_response_item.headers = {"Content-Type": "application/json"}
    batch_response_item.body = BytesIO(b"response body")
    batch_response_item.serialize(writer)
    writer.write_str_value.assert_any_call('id', "12345")
    writer.write_str_value.assert_any_call('atomicity_group', "group1")
    writer.write_int_value.assert_any_call('status', 200)
    writer.write_collection_of_primitive_values.assert_any_call(
        'headers', {"Content-Type": "application/json"}
    )
