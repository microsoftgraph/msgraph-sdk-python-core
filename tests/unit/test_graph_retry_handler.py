import httpx
import pytest
from kiota_abstractions.authentication import AccessTokenProvider

from msgraph.core._enums import FeatureUsageFlag
from msgraph.core.middleware import GraphRequestContext, GraphRetryHandler

# @pytest.mark.trio
# async def test_redirect_handler_send(mock_token_provider):
#     redirect_handler = GraphRetryHandler()

#     req = httpx.Request('GET', "https://httpbin.org/redirect/2")
#     req.context = GraphRequestContext({}, req.headers)
#     resp = await redirect_handler.send(req, mock_transport)

#     assert isinstance(resp, httpx.Response)
#     assert resp.status_code == 302
#     assert  resp.request.context.feature_usage == hex(FeatureUsageFlag.REDIRECT_HANDLER_ENABLED)


@pytest.mark.trio
async def test_no_retry_success_response(mock_transport):
    """
    Test that a request with valid http header and a success response is not retried
    """
    retry_handler = GraphRetryHandler()

    req = httpx.Request('GET', "https://httpbin.org/status/200")
    req.context = GraphRequestContext({}, req.headers)
    resp = await retry_handler.send(req, mock_transport)

    assert isinstance(resp, httpx.Response)
    assert resp.status_code == 200
    assert resp.request.context.feature_usage == hex(FeatureUsageFlag.RETRY_HANDLER_ENABLED)
    with pytest.raises(KeyError):
        resp.request.headers["retry-attempt"]


@pytest.mark.trio
async def test_valid_retry_429(mock_transport):
    """
    Test that a request with valid http header and 503 response is retried
    """
    retry_handler = GraphRetryHandler()

    req = httpx.Request('GET', "https://httpbin.org/status/429")
    req.context = GraphRequestContext({}, req.headers)
    resp = await retry_handler.send(req, mock_transport)

    assert isinstance(resp, httpx.Response)

    assert resp.status_code == 429
    assert resp.request.context.feature_usage == hex(FeatureUsageFlag.RETRY_HANDLER_ENABLED)
    assert int(resp.request.headers["retry-attempt"]) > 0


@pytest.mark.trio
async def test_valid_retry_503(mock_transport):
    """
    Test that a request with valid http header and 503 response is retried
    """
    retry_handler = GraphRetryHandler()

    req = httpx.Request('GET', "https://httpbin.org/status/503")
    req.context = GraphRequestContext({}, req.headers)
    resp = await retry_handler.send(req, mock_transport)

    assert isinstance(resp, httpx.Response)

    assert resp.status_code == 503
    assert resp.request.context.feature_usage == hex(FeatureUsageFlag.RETRY_HANDLER_ENABLED)
    assert int(resp.request.headers["retry-attempt"]) > 0


@pytest.mark.trio
async def test_valid_retry_504(mock_transport):
    """
    Test that a request with valid http header and 503 response is retried
    """
    retry_handler = GraphRetryHandler()

    req = httpx.Request('GET', "https://httpbin.org/status/504")
    req.context = GraphRequestContext({}, req.headers)
    resp = await retry_handler.send(req, mock_transport)

    assert isinstance(resp, httpx.Response)

    assert resp.status_code == 504
    assert resp.request.context.feature_usage == hex(FeatureUsageFlag.RETRY_HANDLER_ENABLED)
    assert int(resp.request.headers["retry-attempt"]) > 0
