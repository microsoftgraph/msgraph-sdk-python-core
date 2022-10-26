import httpx
import pytest
from kiota_abstractions.authentication import AccessTokenProvider

from msgraph.core._enums import FeatureUsageFlag
from msgraph.core.middleware import GraphRedirectHandler, GraphRequestContext


@pytest.mark.trio
async def test_redirect_handler_send(mock_token_provider, mock_request, mock_transport):
    redirect_handler = GraphRedirectHandler()

    req = httpx.Request('GET', "https://httpbin.org/redirect/2")
    req.context = GraphRequestContext({}, req.headers)
    resp = await redirect_handler.send(req, mock_transport)

    assert isinstance(resp, httpx.Response)
    assert resp.status_code == 200
    assert resp.request.context.feature_usage == hex(FeatureUsageFlag.REDIRECT_HANDLER_ENABLED)


@pytest.mark.trio
async def test_redirect_handler_send_max_redirects(
    mock_token_provider, mock_request, mock_transport
):
    redirect_handler = GraphRedirectHandler()

    req = httpx.Request('GET', "https://httpbin.org/redirect/7")
    req.context = GraphRequestContext({}, req.headers)
    with pytest.raises(Exception) as e:
        resp = await redirect_handler.send(req, mock_transport)
