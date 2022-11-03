# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import httpx
import pytest
from kiota_http.middleware import AsyncKiotaTransport, MiddlewarePipeline, RedirectHandler

from msgraph.core import APIVersion, GraphClientFactory, NationalClouds
from msgraph.core.middleware.telemetry import GraphTelemetryHandler


def test_create_with_default_middleware():
    """Test creation of GraphClient using default middleware"""
    client = GraphClientFactory.create_with_default_middleware()

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)
    pipeline = client._transport.pipeline
    assert isinstance(pipeline, MiddlewarePipeline)
    assert isinstance(pipeline._first_middleware, RedirectHandler)
    assert isinstance(pipeline._current_middleware, GraphTelemetryHandler)


def test_create_with_custom_middleware():
    """Test creation of HTTP Clients with custom middleware"""
    middleware = [
        GraphTelemetryHandler(),
    ]
    client = GraphClientFactory.create_with_custom_middleware(middleware=middleware)

    assert isinstance(client, httpx.AsyncClient)
    assert isinstance(client._transport, AsyncKiotaTransport)
    pipeline = client._transport.pipeline
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
