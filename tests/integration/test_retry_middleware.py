import pytest

from msgraphcore.graph_session import GraphSession

RETRY_CONFIG = {"retry_total": 2, "retry_backoff_factor": 0.1}


@pytest.fixture(scope="module")
def graph_session():
    scopes = ['user.read']
    credential = _CustomTokenCredential()
    return GraphSession(credential, scopes, retry_config=RETRY_CONFIG)


class _CustomTokenCredential:
    def get_token(self, scopes):
        return ['{token:https://graph.microsoft.com/}']


def test_middleware_pipeline(graph_session):
    """
    Test that the middleware pipeline works as expected
    """
    response = graph_session.get(
        'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
    )
    assert response.status_code == 200


def test_no_retry_success_response(graph_session):
    """
    Test that a request with valid http header and a success response is not retried
    """
    response = graph_session.get(
        'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
    )

    assert response.status_code == 200
    assert response.request.headers["Retry-Attempt"] == "0"


def test_valid_retry_429(graph_session):
    """
    Test that a request with valid http header and 503 response is retried
    """
    response = graph_session.get('https://httpbin.org/status/429')

    assert response.status_code == 429

    assert response.request.headers["Retry-Attempt"] == '2'


def test_valid_retry_503(graph_session):
    """
    Test that a request with valid http header and 503 response is retried
    """
    response = graph_session.get('https://httpbin.org/status/503')

    assert response.status_code == 503
    assert response.request.headers["Retry-Attempt"] == "2"


def test_valid_retry_504(graph_session):
    """
    Test that a request with valid http header and 503 response is retried
    """
    response = graph_session.get('https://httpbin.org/status/504')

    assert response.status_code == 504
    assert response.request.headers["Retry-Attempt"] == "2"


def test_request_specific_options_override_default(graph_session):
    """
    Test that retry options passed to the request take precedence over
    the default options.
    """
    response_1 = graph_session.get('https://httpbin.org/status/429')
    response_2 = graph_session.get(
        'https://httpbin.org/status/503', retry_config={'retry_total': 1}
    )
    response_3 = graph_session.get('https://httpbin.org/status/504')
    response_4 = graph_session.get(
        'https://httpbin.org/status/429', retry_config={'retry_total': 0}
    )

    assert response_1.status_code == 429
    assert response_1.request.headers["Retry-Attempt"] == "2"
    assert response_2.status_code == 503
    assert response_2.request.headers["Retry-Attempt"] == "1"
    assert response_3.status_code == 504
    assert response_3.request.headers["Retry-Attempt"] == "2"
    assert response_4.status_code == 429
    assert response_4.request.headers["Retry-Attempt"] == "0"


def test_retries_time_limit(graph_session):
    """
    Test that the cumulative retry time plus the retry-after values does not exceed the
    provided retries time limit
    """

    response = graph_session.get(
        'https://httpbin.org/status/503', retry_config={'retry_time_limit': 0.1}
    )

    assert response.status_code == 503
    headers = response.request.headers
    assert headers["Retry-Attempt"] == "0"
