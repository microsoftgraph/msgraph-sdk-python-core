# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import httpx
import pytest
from asyncmock import AsyncMock

from msgraph.core import APIVersion, GraphClient, NationalClouds
from msgraph.core.middleware.authorization import GraphAuthorizationHandler


def test_initialize_graph_client_with_default_middleware(mock_token_provider):
    """
    Test creating a graph client with default middleware works as expected
    """

    graph_client = GraphClient(token_provider=mock_token_provider)

    assert isinstance(graph_client.client, httpx.AsyncClient)
    assert str(graph_client.client.base_url) == f'{NationalClouds.Global}/{APIVersion.v1}/'


def test_initialize_graph_client_with_custom_middleware(mock_token_provider):
    """
    Test creating a graph client with custom middleware works as expected
    """
    middleware = [
        GraphAuthorizationHandler(token_provider=mock_token_provider),
    ]
    graph_client = GraphClient(middleware=middleware)

    assert isinstance(graph_client.client, httpx.AsyncClient)
    assert str(graph_client.client.base_url) == f'{NationalClouds.Global}/{APIVersion.v1}/'


def test_initialize_graph_client_both_token_provider_and_custom_middleware(mock_token_provider):
    """
    Test creating a graph client with both token provider and custom middleware throws an error
    """
    middleware = [
        GraphAuthorizationHandler(token_provider=mock_token_provider),
    ]
    with pytest.raises(Exception):
        graph_client = GraphClient(token_provider=mock_token_provider, middleware=middleware)


def test_initialize_graph_client_without_token_provider_or_custom_middleware():
    """
    Test creating a graph client with default middleware works as expected
    """

    with pytest.raises(Exception):
        graph_client = GraphClient()


def test_graph_client_with_custom_configuration(mock_token_provider):
    """
    Test creating a graph client with custom middleware works as expected
    """
    graph_client = GraphClient(
        token_provider=mock_token_provider,
        api_version=APIVersion.beta,
        base_url=NationalClouds.China
    )

    assert str(graph_client.client.base_url) == f'{NationalClouds.China}/{APIVersion.beta}/'


def test_graph_client_uses_same_session(mock_token_provider):
    """
    Test graph client is a singleton class and uses the same session
    """
    graph_client1 = GraphClient(token_provider=mock_token_provider)

    graph_client2 = GraphClient(token_provider=mock_token_provider)
    assert graph_client1 is graph_client2
