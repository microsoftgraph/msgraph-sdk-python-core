import pytest

from msgraphcore.graph_session import GraphSession

URL = 'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'


@pytest.fixture
def graph_session():
    scopes = ['user.read']
    credential = _CustomTokenCredential()
    session = GraphSession(credential, scopes)
    return session


class _CustomTokenCredential:
    def get_token(self, scopes):
        return ['{token:https://graph.microsoft.com/}']


def test_no_retry_success_response(graph_session):
    """
    Test that a request with valid http header and a success response is not retried
    """
    response = graph_session.get(
        'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
    )
    assert response.status_code == 200
    headers = response.request.headers
    assert headers["Retry-Attempt"] == "0"


def test_valid_retry_429(graph_session):
    """
    Test that a request with valid http header and 503 response is retried
    """
    response = graph_session.get('https://httpbin.org/status/429')
    assert response.status_code == 429
    headers = response.request.headers
    print(headers)
    assert headers["Retry-Attempt"] == "3"


def test_valid_retry_503(graph_session):
    """
    Test that a request with valid http header and 503 response is retried
    """
    response = graph_session.get('https://httpbin.org/status/503')
    assert response.status_code == 503
    headers = response.request.headers
    assert headers["Retry-Attempt"] == "3"


def test_valid_retry_504(graph_session):
    """
    Test that a request with valid http header and 503 response is retried
    """
    response = graph_session.get('https://httpbin.org/status/504')
    assert response.status_code == 504
    headers = response.request.headers
    assert headers["Retry-Attempt"] == "3"
