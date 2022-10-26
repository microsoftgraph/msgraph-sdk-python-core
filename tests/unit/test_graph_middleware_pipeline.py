# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import httpx
import pytest

from msgraph.core.middleware import GraphMiddlewarePipeline, GraphRequestContext


@pytest.mark.trio
async def test_middleware_pipeline_send(mock_transport, mock_request):
    pipeline = GraphMiddlewarePipeline(mock_transport)
    response = await pipeline.send(mock_request)

    assert isinstance(response, httpx.Response)
    assert 'request_options' not in response.request.headers
    assert isinstance(response.request.context, GraphRequestContext)
