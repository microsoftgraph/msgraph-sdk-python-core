import platform
import re
import uuid

import pytest

from msgraph.core import SDK_VERSION, APIVersion, GraphClient, NationalClouds

BASE_URL = NationalClouds.Global + '/' + APIVersion.v1


@pytest.fixture
def graph_client():
    scopes = ['user.read']
    credential = _CustomTokenCredential()
    client = GraphClient(credential=credential, scopes=scopes)
    return client


class _CustomTokenCredential:
    def get_token(self, scopes):
        return ['{token:https://graph.microsoft.com/}']


def test_telemetry_handler(graph_client):
    """
    Test telemetry handler updates the graph request with the requisite headers
    """
    response = graph_client.get('https://graph.microsoft.com/v1.0/me')
    system = platform.system()
    version = platform.version()
    host_os = f'{system} {version}'
    python_version = platform.python_version()
    runtime_environment = f'Python/{python_version}'

    assert response.status_code == 401
    assert response.request.headers["client-request-id"]
    assert response.request.headers["sdkVersion"].startswith('graph-python-core/' + SDK_VERSION)
    assert response.request.headers["HostOs"] == host_os
    assert response.request.headers["RuntimeEnvironment"] == runtime_environment


def test_telemetry_handler_non_graph_url(graph_client):
    """
    Test telemetry handler does not updates the request headers for non-graph requests
    """
    response = graph_client.get('https://httpbin.org/status/200')

    assert response.status_code == 200
    with pytest.raises(KeyError):
        response.request.headers["client-request-id"]
        response.request.headers["sdkVersion"]
        response.request.headers["HostOs"]
        response.request.headers["RuntimeEnvironment"]


def test_custom_client_request_id(graph_client):
    """
    Test customer provided client request id overrides default value
    """
    custom_id = str(uuid.uuid4())
    response = graph_client.get(
        'https://httpbin.org/status/200', headers={"client-request-id": custom_id}
    )

    assert response.status_code == 200
    assert response.request.headers["client-request-id"] == custom_id
    with pytest.raises(KeyError):
        response.request.headers["client-request-id"]
        response.request.headers["sdkVersion"]
        response.request.headers["HostOs"]
        response.request.headers["RuntimeEnvironment"]
