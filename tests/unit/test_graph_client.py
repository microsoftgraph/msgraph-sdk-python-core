# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
import responses
from requests import Session
from requests.adapters import HTTPAdapter

from msgraph.core.constants import CONNECTION_TIMEOUT, REQUEST_TIMEOUT
from msgraph.core.enums import APIVersion, NationalClouds
from msgraph.core.graph_client import GraphClient
from msgraph.core.middleware.authorization import AuthorizationHandler
from msgraph.core.middleware.middleware import BaseMiddleware, MiddlewarePipeline


def test_graph_client_with_default_middleware():
    """
    Test creating a graph client with default middleware works as expected
    """
    credential = _CustomTokenCredential()
    client = GraphClient(credential=credential)

    assert isinstance(client.graph_session, Session)
    assert isinstance(client.graph_session.get_adapter('https://'), HTTPAdapter)
    assert client.graph_session.base_url == NationalClouds.Global + '/' + APIVersion.v1


def test_graph_client_with_custom_middleware():
    """
    Test creating a graph client with custom middleware works as expected
    """
    credential = _CustomTokenCredential()
    middleware = [
        AuthorizationHandler(credential),
    ]
    client = GraphClient(middleware=middleware)

    assert isinstance(client.graph_session, Session)
    assert isinstance(client.graph_session.get_adapter('https://'), HTTPAdapter)
    assert client.graph_session.base_url == NationalClouds.Global + '/' + APIVersion.v1


def test_graph_client_with_custom_configuration():
    """
    Test creating a graph client with custom middleware works as expected
    """
    credential = _CustomTokenCredential()
    client = GraphClient(
        credential=credential, api_version=APIVersion.beta, cloud=NationalClouds.China
    )

    assert client.graph_session.base_url == NationalClouds.China + '/' + APIVersion.beta


def test_graph_client_uses_same_session():
    """
    Test graph client is a singleton class and uses the same session
    """
    credential = _CustomTokenCredential()
    client = GraphClient(credential=credential)

    client2 = GraphClient(credential=credential)
    assert client is client2


@responses.activate
def test_graph_client_builds_graph_urls():
    """
    Test that the graph client builds full urls if supplied with partial
    """
    credential = _CustomTokenCredential()
    client = GraphClient(credential=credential)
    graph_url = client.graph_session.base_url + '/me'

    responses.add(responses.GET, graph_url, status=200)

    client.get('/me', headers={})
    assert graph_url == responses.calls[0].request.url


@responses.activate
def test_does_not_build_graph_urls_for_full_urls():
    """
    Test that the graph client builds full urls if supplied with partial
    """
    other_url = 'https://microsoft.com/'
    responses.add(responses.GET, other_url, status=200)

    credential = _CustomTokenCredential()
    client = GraphClient(credential=credential)
    client.get(other_url, headers={})
    request_url = responses.calls[0].request.url
    assert other_url == request_url


class _CustomTokenCredential:
    def get_token(self, scopes):
        return ['{token:https://graph.microsoft.com/}']
