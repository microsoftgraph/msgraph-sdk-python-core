import platform

import pytest

from msgraphcore.constants import BASE_URL, SDK_VERSION
from msgraphcore.graph_session import GraphSession


@pytest.fixture
def graph_session():
    scopes = ['user.read']
    credential = _CustomTokenCredential()
    session = GraphSession(credential, scopes)
    return session


class _CustomTokenCredential:
    def get_token(self, scopes):
        return ['{token:https://graph.microsoft.com/}']


def test_telemetry_handler(graph_session):
    """
    Test telemetry handler updates the graph request with the requisite headers
    """
    response = graph_session.get(
        'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
    )
    system = platform.system()
    version = platform.version()
    host_os = f'{system} {version}'
    python_version = platform.python_version()
    runtime_environment = f'Python/{python_version}'

    assert response.status_code == 200
    assert response.request.headers["client-request-id"]
    assert response.request.headers["sdkVersion"].startswith('graph-python-core/' + SDK_VERSION)
    assert response.request.headers["HostOs"] == host_os
    assert response.request.headers["RuntimeEnvironment"] == runtime_environment
