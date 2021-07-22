# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest
from azure.identity import EnvironmentCredential
from requests import Session

from msgraph.core import APIVersion, GraphClient
from msgraph.core.middleware.authorization import AuthorizationHandler


def test_graph_client_with_default_middleware():
    """
    Test that a graph client uses default middleware if none are provided
    """
    # credential = _CustomTokenCredential()
    client = GraphClient(credential=EnvironmentCredential())
    response = client.get('https://graph.microsoft.com/v1.0/users')
    assert response.status_code == 200


def test_graph_client_with_user_provided_session():
    """
    Test that the graph client works with a user provided session object
    """

    session = Session()
    client = GraphClient(session=session, credential=EnvironmentCredential())
    response = client.get('https://graph.microsoft.com/v1.0/users', )
    assert response.status_code == 200


def test_graph_client_with_custom_settings():
    """
    Test that the graph client works with user provided configuration
    """
    credential = EnvironmentCredential()
    client = GraphClient(api_version=APIVersion.beta, credential=credential)
    response = client.get('https://graph.microsoft.com/v1.0/users', )
    assert response.status_code == 200


def test_graph_client_with_custom_middleware():
    """
    Test client factory works with user provided middleware
    """
    credential = EnvironmentCredential()
    middleware = [
        AuthorizationHandler(credential),
    ]
    client = GraphClient(middleware=middleware)
    response = client.get('https://graph.microsoft.com/v1.0/users', )
    assert response.status_code == 200


def test_graph_client_adds_context_to_request():
    """
    Test the graph client adds a context object to a request
    """
    credential = EnvironmentCredential()
    scopes = ['https://graph.microsoft.com/.default']
    client = GraphClient(credential=credential)
    response = client.get('https://graph.microsoft.com/v1.0/users', scopes=scopes)
    assert response.status_code == 200
    assert hasattr(response.request, 'context')


def test_graph_client_picks_options_from_kwargs():
    """
    Test the graph client picks middleware options from kwargs and sets them in the context
    """
    credential = EnvironmentCredential()
    scopes = ['https://graph.microsoft.com/.default']
    client = GraphClient(credential=credential)
    response = client.get('https://graph.microsoft.com/v1.0/users', scopes=scopes)
    assert response.status_code == 200
    assert 'scopes' in response.request.context.middleware_control.keys()
    assert response.request.context.middleware_control['scopes'] == scopes


def test_graph_client_allows_passing_optional_kwargs():
    """
    Test the graph client allows passing optional kwargs native to the requests library
    such as stream, proxy and cert.
    """
    credential = EnvironmentCredential()
    scopes = ['https://graph.microsoft.com/.default']
    client = GraphClient(credential=credential)
    response = client.get('https://graph.microsoft.com/v1.0/users', scopes=scopes, stream=True)
    assert response.status_code == 200
