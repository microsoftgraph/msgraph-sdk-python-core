# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import httpx
import pytest
from kiota_abstractions.authentication import AccessTokenProvider

from msgraph.core._enums import FeatureUsageFlag
from msgraph.core.middleware import GraphAuthorizationHandler, GraphRequestContext


def test_auth_handler_initialization(mock_token_provider):
    auth_handler = GraphAuthorizationHandler(mock_token_provider)
    assert isinstance(auth_handler.token_provider, AccessTokenProvider)


@pytest.mark.trio
async def test_auth_handler_send(mock_token_provider, mock_request, mock_transport):
    auth_handler = GraphAuthorizationHandler(mock_token_provider)
    resp = await auth_handler.send(mock_request, mock_transport)
    assert isinstance(resp, httpx.Response)
    assert resp.status_code == 200
    assert 'Authorization' in resp.request.headers
    assert resp.request.context.feature_usage == hex(FeatureUsageFlag.AUTH_HANDLER_ENABLED)
