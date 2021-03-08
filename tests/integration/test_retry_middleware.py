import pytest

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


def test_no_retry_success_response(graph_session):
    """
    Test that a request with valid http header and a success response is not retried
    """
    response = graph_session.get(
        'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'
    )

    assert response.status_code == 200
    assert response.request.headers["Retry-Attempt"] == "0"
