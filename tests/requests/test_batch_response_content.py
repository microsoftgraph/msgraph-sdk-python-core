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


def test_get_response_stream_by_id_none(batch_response_content):
    batch_response_content.get_response_by_id = Mock(return_value=None)
    result = batch_response_content.get_response_stream_by_id('1')
    assert result is None


def test_get_response_stream_by_id_body_none(batch_response_content):
    batch_response_content.get_response_by_id = Mock(return_value=Mock(body=None))
    result = batch_response_content.get_response_stream_by_id('1')
    assert result is None


def test_get_response_stream_by_id_bytesio(batch_response_content):
    batch_response_content.get_response_by_id = Mock(
        return_value=Mock(body=BytesIO(b'Hello, world!'))
    )
    result = batch_response_content.get_response_stream_by_id('2')
    assert isinstance(result, BytesIO)
    assert result.read() == b'Hello, world!'


def test_get_response_stream_by_id_bytes(batch_response_content):
    batch_response_content.get_response_by_id = Mock(return_value=Mock(body=b'Hello, world!'))
    result = batch_response_content.get_response_stream_by_id('1')
    assert isinstance(result, BytesIO)
    assert result.read() == b'Hello, world!'


def test_get_response_status_codes_none(batch_response_content):
    batch_response_content._responses = None
    result = batch_response_content.get_response_status_codes()
    assert result == {}


def test_get_response_status_codes(batch_response_content):
    batch_response_content._responses = {
        '1': Mock(status=200),
        '2': Mock(status=404),
        '3': Mock(status=500),
    }
    result = batch_response_content.get_response_status_codes()
    expected = {
        '1': 200,
        '2': 404,
        '3': 500,
    }
    assert result == expected


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
