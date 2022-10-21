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

# def test_initialize_with_custom_config():
#     """Test creation of HTTP Client will use custom configuration if they are passed"""
#     client = HTTPClientFactory(api_version=APIVersion.beta, timeout=(5, 5))

#     assert client.api_version == APIVersion.beta
#     assert client.endpoint == NationalClouds.Global
#     assert client.timeout == (5, 5)
#     assert isinstance(client.session, Session)


def test_create_with_default_middleware(mock_token_provider):
    """Test creation of GraphClient using default middleware"""
    client = GraphClientFactory(
        api_version=APIVersion.beta,
        timeout=httpx.Timeout(
            5,
            connect=5,
        ),
        endpoint=NationalClouds.Global,
        client=None
    ).create_with_default_middleware(token_provider=mock_token_provider)

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)
    assert str(client.base_url) == f'{NationalClouds.Global}/{APIVersion.beta}/'


def test_create_with_custom_middleware(mock_token_provider):
    """Test creation of HTTP Clients with custom middleware"""
    middleware = [
        GraphAuthorizationHandler(mock_token_provider),
    ]
    client = GraphClientFactory(
        api_version=APIVersion.v1,
        timeout=httpx.Timeout(
            5,
            connect=5,
        ),
        endpoint=NationalClouds.Global,
        client=None
    ).create_with_custom_middleware(middleware=middleware)

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)
    assert str(client.base_url) == f'{NationalClouds.Global}/{APIVersion.v1}/'


def test_get_base_url():
    """
    Test base url is formed by combining the national cloud endpoint with
    Api version
    """
    client = GraphClientFactory(
        api_version=APIVersion.beta,
        endpoint=NationalClouds.Germany,
        timeout=httpx.Timeout(
            5,
            connect=5,
        ),
        client=None
    )
    assert client._get_base_url() == f'{NationalClouds.Germany}/{APIVersion.beta}'


def test_get_default_middleware(mock_token_provider):
    client = GraphClientFactory(
        api_version=APIVersion.beta,
        endpoint=NationalClouds.Germany,
        timeout=httpx.Timeout(
            5,
            connect=5,
        ),
        client=None
    )
    middleware = client._get_default_middleware(mock_token_provider, httpx.AsyncClient()._transport)

    assert isinstance(middleware, GraphMiddlewarePipeline)
