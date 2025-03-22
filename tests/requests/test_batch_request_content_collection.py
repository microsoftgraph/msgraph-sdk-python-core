import pytest
from io import BytesIO
from kiota_abstractions.request_information import RequestInformation
from msgraph_core.requests.batch_request_item import BatchRequestItem
from msgraph_core.requests.batch_request_content_collection import BatchRequestContentCollection
from kiota_abstractions.headers_collection import HeadersCollection as RequestHeaders


@pytest.fixture
def batch_request_content_collection():
    return BatchRequestContentCollection()


@pytest.fixture
def request_info():
    request_info = RequestInformation()
    request_info.http_method = "GET"
    request_info.url = "https://graph.microsoft.com/v1.0/me"
    request_info.headers = RequestHeaders()
    request_info.headers.add("Content-Type", "application/json")
    request_info.content = BytesIO(b'{"key": "value"}')
    return request_info


@pytest.fixture
def batch_request_item1(request_info):
    return BatchRequestItem(request_information=request_info, id="1")


@pytest.fixture
def batch_request_item2(request_info):
    return BatchRequestItem(request_information=request_info, id="2")


def test_init_batches(batch_request_content_collection):
    assert len(batch_request_content_collection.batches) == 1
    assert batch_request_content_collection.current_batch is not None


def test_add_batch_request_item(batch_request_content_collection, batch_request_item1, batch_request_item2):
    batch_request_content_collection.add_batch_request_item(batch_request_item1)
    batch_request_content_collection.add_batch_request_item(batch_request_item2)
    assert len(batch_request_content_collection.batches) == 1
    assert len(batch_request_content_collection.current_batch.requests) == 2
