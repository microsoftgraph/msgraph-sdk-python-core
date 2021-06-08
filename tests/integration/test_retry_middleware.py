import pytest

from msgraph.core import GraphClient


@pytest.fixture
def graph_client():
    scopes = ['user.read']
    credential = _CustomTokenCredential()
    client = GraphClient(credential=credential, scopes=scopes)
    return client


class _CustomTokenCredential:
    def get_token(self, scopes):
        return ['{token:https://graph.microsoft.com/}']


def test_no_retry_success_response(graph_client):
    """
    Test that a request with valid http header and a success response is not retried
    """
    response = graph_client.get(
        'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
    )

    assert response.status_code == 200
    assert response.request.headers["Retry-Attempt"] == "0"


def test_valid_retry_429(graph_client):
    """
    Test that a request with valid http header and 503 response is retried
    """
    response = graph_client.get('https://httpbin.org/status/429')

    assert response.status_code == 429
    assert response.request.headers["Retry-Attempt"] == "3"


def test_valid_retry_503(graph_client):
    """
    Test that a request with valid http header and 503 response is retried
    """
    response = graph_client.get('https://httpbin.org/status/503')

    assert response.status_code == 503
    assert response.request.headers["Retry-Attempt"] == "3"


def test_valid_retry_504(graph_client):
    """
    Test that a request with valid http header and 503 response is retried
    """
    response = graph_client.get('https://httpbin.org/status/504')

    assert response.status_code == 504
    assert response.request.headers["Retry-Attempt"] == "3"


def test_request_specific_options_override_default(graph_client):
    """
    Test that retry options passed to the request take precedence over
    the default options.
    """
    response_1 = graph_client.get('https://httpbin.org/status/429')
    response_2 = graph_client.get('https://httpbin.org/status/503', retry_total=2)
    response_3 = graph_client.get('https://httpbin.org/status/504')
    response_4 = graph_client.get('https://httpbin.org/status/429', retry_total=1)

    assert response_1.status_code == 429
    assert response_1.request.headers["Retry-Attempt"] == "3"
    assert response_2.status_code == 503
    assert response_2.request.headers["Retry-Attempt"] == "2"
    assert response_3.status_code == 504
    assert response_3.request.headers["Retry-Attempt"] == "3"
    assert response_4.status_code == 429
    assert response_4.request.headers["Retry-Attempt"] == "1"


def test_retries_time_limit(graph_client):
    """
    Test that the cumulative retry time plus the retry-after values does not exceed the
    provided retries time limit
    """

    response = graph_client.get('https://httpbin.org/status/503', retry_time_limit=0.1)

    assert response.status_code == 503
    headers = response.request.headers
    assert headers["Retry-Attempt"] == "0"
