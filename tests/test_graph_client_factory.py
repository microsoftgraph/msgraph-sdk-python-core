# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import httpx
import pytest
from kiota_http.middleware import MiddlewarePipeline, RedirectHandler, RetryHandler
from kiota_http.middleware.options import RedirectHandlerOption, RetryHandlerOption

from msgraph_core import APIVersion, GraphClientFactory, NationalClouds
from msgraph_core.middleware import AsyncGraphTransport, GraphTelemetryHandler


def test_create_with_default_middleware():
    """Test creation of GraphClient using default middleware"""
    client = GraphClientFactory.create_with_default_middleware()

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncGraphTransport)
    pipeline = client._transport.pipeline
    assert isinstance(pipeline, MiddlewarePipeline)
    assert isinstance(pipeline._first_middleware, RedirectHandler)
    assert isinstance(pipeline._current_middleware, GraphTelemetryHandler)
    
def test_create_with_default_middleware_custom_client():
    """Test creation of GraphClient using default middleware"""
    timeout = httpx.Timeout(20, connect=10)
    custom_client = httpx.AsyncClient(timeout=timeout, http2=True)
    client = GraphClientFactory.create_with_default_middleware(client=custom_client)

    assert isinstance(client, httpx.AsyncClient)
    assert client.timeout == httpx.Timeout(connect=10, read=20, write=20, pool=20)
    assert isinstance(client._transport, AsyncGraphTransport)
    pipeline = client._transport.pipeline
    assert isinstance(pipeline, MiddlewarePipeline)
    assert isinstance(pipeline._first_middleware, RedirectHandler)
    assert isinstance(pipeline._current_middleware, GraphTelemetryHandler)
    
def test_create_with_default_middleware_custom_client_with_proxy():
    """Test creation of GraphClient using default middleware"""
    proxies = {
        "http://": "http://localhost:8030",
        "https://": "http://localhost:8031",
    }
    timeout = httpx.Timeout(20, connect=10)
    custom_client = httpx.AsyncClient(timeout=timeout, http2=True, proxies=proxies)
    client = GraphClientFactory.create_with_default_middleware(client=custom_client)

    assert isinstance(client, httpx.AsyncClient)
    assert client.timeout == httpx.Timeout(connect=10, read=20, write=20, pool=20)
    assert isinstance(client._transport, AsyncGraphTransport)
    pipeline = client._transport.pipeline
    assert isinstance(pipeline, MiddlewarePipeline)
    assert isinstance(pipeline._first_middleware, RedirectHandler)
    assert isinstance(pipeline._current_middleware, GraphTelemetryHandler)
    assert client._mounts
    for pattern, transport in client._mounts.items():
        assert isinstance(transport, AsyncGraphTransport)


def test_create_default_with_custom_middleware():
    """Test creation of HTTP Client using default middleware and custom options"""
    retry_options = RetryHandlerOption(max_retries=5)
    options = {f'{retry_options.get_key()}': retry_options}
    client = GraphClientFactory.create_with_default_middleware(options=options)

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncGraphTransport)
    pipeline = client._transport.pipeline
    assert isinstance(pipeline, MiddlewarePipeline)
    assert isinstance(pipeline._first_middleware, RedirectHandler)
    retry_handler = pipeline._first_middleware.next
    assert isinstance(retry_handler, RetryHandler)
    assert retry_handler.options.max_retry == retry_options.max_retry
    assert isinstance(pipeline._current_middleware, GraphTelemetryHandler)


def test_create_with_custom_middleware_custom_client():
    """Test creation of HTTP Clients with custom middleware"""
    timeout = httpx.Timeout(20, connect=10)
    custom_client = httpx.AsyncClient(timeout=timeout, http2=True)
    middleware = [
        GraphTelemetryHandler(),
    ]
    client = GraphClientFactory.create_with_custom_middleware(
        middleware=middleware, client=custom_client
    )

    assert isinstance(client, httpx.AsyncClient)
    assert client.timeout == httpx.Timeout(connect=10, read=20, write=20, pool=20)
    assert isinstance(client._transport, AsyncGraphTransport)
    pipeline = client._transport.pipeline
    assert isinstance(pipeline._first_middleware, GraphTelemetryHandler)
    
def test_create_with_custom_middleware_custom_client_with_proxy():
    """Test creation of HTTP Clients with custom middleware"""
    proxies = {
        "http://": "http://localhost:8030",
        "https://": "http://localhost:8031",
    }
    timeout = httpx.Timeout(20, connect=10)
    custom_client = httpx.AsyncClient(timeout=timeout, http2=True, proxies=proxies)
    middleware = [
        GraphTelemetryHandler(),
    ]
    client = GraphClientFactory.create_with_custom_middleware(
        middleware=middleware, client=custom_client
    )

    assert isinstance(client, httpx.AsyncClient)
    assert client.timeout == httpx.Timeout(connect=10, read=20, write=20, pool=20)
    assert isinstance(client._transport, AsyncGraphTransport)
    pipeline = client._transport.pipeline
    assert isinstance(pipeline._first_middleware, GraphTelemetryHandler)
    assert client._mounts
    for pattern, transport in client._mounts.items():
        assert isinstance(transport, AsyncGraphTransport)
        pipeline = transport.pipeline
        assert isinstance(pipeline._first_middleware, GraphTelemetryHandler)


def test_graph_client_factory_with_custom_configuration():
    """
    Test creating a graph client with custom url overrides the default
    """
    graph_client = GraphClientFactory.create_with_default_middleware(
        api_version=APIVersion.beta, host=NationalClouds.China
    )
    assert isinstance(graph_client, httpx.AsyncClient)
    assert str(graph_client.base_url) == f'{NationalClouds.China}/{APIVersion.beta}/'


def test_get_base_url():
    """
    Test base url is formed by combining the national cloud endpoint with
    Api version
    """
    url = GraphClientFactory._get_base_url(
        host=NationalClouds.Germany,
        api_version=APIVersion.beta,
    )
    assert url == f'{NationalClouds.Germany}/{APIVersion.beta}'
