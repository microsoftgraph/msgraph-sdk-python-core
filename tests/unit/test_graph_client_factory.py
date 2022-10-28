# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import httpx
import pytest
from kiota_http.middleware import AsyncKiotaTransport

from msgraph.core import APIVersion, GraphClientFactory, NationalClouds
from msgraph.core._constants import DEFAULT_CONNECTION_TIMEOUT, DEFAULT_REQUEST_TIMEOUT
from msgraph.core.middleware import GraphAuthorizationHandler
from msgraph.core.middleware.middleware import GraphMiddlewarePipeline
from msgraph.core.middleware.redirect import GraphRedirectHandler
from msgraph.core.middleware.retry import GraphRetryHandler
from msgraph.core.middleware.telemetry import GraphTelemetryHandler


def test_create_with_default_middleware_no_auth_provider():
    """Test creation of GraphClient without a token provider does not
    add the Authorization middleware"""
    client = GraphClientFactory.create_with_default_middleware(client=httpx.AsyncClient())

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)
    pipeline = client._transport.middleware
    assert isinstance(pipeline, GraphMiddlewarePipeline)
    assert not isinstance(pipeline._first_middleware, GraphAuthorizationHandler)


def test_create_with_default_middleware(mock_token_provider):
    """Test creation of GraphClient using default middleware and passing a token
    provider adds Authorization middleware"""
    client = GraphClientFactory.create_with_default_middleware(
        client=httpx.AsyncClient(), token_provider=mock_token_provider
    )

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)
    pipeline = client._transport.middleware
    assert isinstance(pipeline, GraphMiddlewarePipeline)
    assert isinstance(pipeline._first_middleware, GraphAuthorizationHandler)


def test_create_with_custom_middleware(mock_token_provider):
    """Test creation of HTTP Clients with custom middleware"""
    middleware = [
        GraphTelemetryHandler(),
    ]
    client = GraphClientFactory.create_with_custom_middleware(
        client=httpx.AsyncClient(), middleware=middleware
    )

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)
    pipeline = client._transport.middleware
    assert isinstance(pipeline._first_middleware, GraphTelemetryHandler)


def test_get_common_middleware():
    middleware = GraphClientFactory._get_common_middleware()

    assert len(middleware) == 3
    assert isinstance(middleware[0], GraphRedirectHandler)
    assert isinstance(middleware[1], GraphRetryHandler)
    assert isinstance(middleware[2], GraphTelemetryHandler)
