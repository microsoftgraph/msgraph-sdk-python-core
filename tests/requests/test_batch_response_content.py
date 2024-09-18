import pytest
from unittest.mock import Mock
from io import BytesIO
from kiota_abstractions.serialization import ParseNode, SerializationWriter, Parsable, ParseNodeFactoryRegistry
from msgraph_core.requests.batch_response_item import BatchResponseItem
from msgraph_core.requests.batch_response_content import BatchResponseContent


@pytest.fixture
def batch_response_content():
    return BatchResponseContent()


def test_initialization(batch_response_content):
    assert batch_response_content.responses == {}
    assert isinstance(batch_response_content._responses, dict)


def test_responses_property(batch_response_content):
    response_item = Mock(spec=BatchResponseItem)
    batch_response_content.responses = [response_item]
    assert batch_response_content.responses == [response_item]


def test_response_method(batch_response_content):
    response_item = Mock(spec=BatchResponseItem)
    response_item.request_id = "12345"
    batch_response_content.responses = {"12345": response_item}
    assert batch_response_content.get_response_by_id("12345") == response_item


def test_response_body_method(batch_response_content):
    response_item = Mock(spec=BatchResponseItem)
    response_item.request_id = "12345"
    response_item.content_type = "application/json"
    response_item.body = BytesIO(b'{"key": "value"}')
    batch_response_content.responses = [response_item]

    parse_node = Mock(spec=ParseNode)
    parse_node.get_object_value.return_value = {"key": "value"}
    registry = Mock(spec=ParseNodeFactoryRegistry)
    registry.get_root_parse_node.return_value = parse_node

    with pytest.raises(ValueError):
        batch_response_content.response_body("12345", dict)


def test_get_field_deserializers(batch_response_content):
    deserializers = batch_response_content.get_field_deserializers()
    assert isinstance(deserializers, dict)
    assert "responses" in deserializers


def test_serialize(batch_response_content):
    writer = Mock(spec=SerializationWriter)
    response_item = Mock(spec=BatchResponseItem)
    batch_response_content.responses = {"12345": response_item}
    batch_response_content.serialize(writer)
    writer.write_collection_of_object_values.assert_called_once_with('responses', [response_item])


def test_create_from_discriminator_value():
    parse_node = Mock(spec=ParseNode)
    batch_response_content = BatchResponseContent.create_from_discriminator_value(parse_node)
    assert isinstance(batch_response_content, BatchResponseContent)
