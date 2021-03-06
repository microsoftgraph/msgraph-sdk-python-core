import pytest
import responses

from msgraphcore.graph_session import GraphSession
from msgraphcore.middleware.retry_middleware import RetryMiddleware


class CustomTokenCredential:
    def get_token(self, scopes):
        return ['{token:https://graph.microsoft.com/}']


@pytest.fixture
def session():
    session_object = GraphSession(CustomTokenCredential(), ['user.read'])
    return session_object


def test_no_config():
    """
    Test that default values are used if no custom confguration is passed
    """
    retry_handler = RetryMiddleware(retry_configs={})
    assert retry_handler.total_retries == 5
    assert retry_handler.timeout == 604800
    assert retry_handler.backoff_max == 120
    assert retry_handler.backoff_factor == 0.1
    assert retry_handler._allowed_methods == frozenset(
        ['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE']
    )
    assert retry_handler._respect_retry_after_header
    assert retry_handler._retry_on_status_codes == {429, 503, 504}


def test_custom_config():
    """
    Test that default configuration is overrriden if custom configuration is provided
    """
    custom_configs = {
        "retry_total": 10,
        "retry_backoff_factor": 0.2,
        "retry_backoff_max": 200,
        "timeout": 100,
        "retry_on_status_codes": [502, 503],
    }

    retry_handler = RetryMiddleware(retry_configs=custom_configs)
    assert retry_handler.total_retries == 10
    assert retry_handler.timeout == 100
    assert retry_handler.backoff_max == 200
    assert retry_handler.backoff_factor == 0.2
    assert retry_handler._retry_on_status_codes == {429, 502, 503, 504}


def test_diable_retries():
    """
    Test that when disable retries is called, total retries are set to zero
    """
    retry_handler = RetryMiddleware.disable_retries()
    assert retry_handler.total_retries == 0
    retry_settings = retry_handler.configure_retry_settings()
    assert not retry_handler.increment_counter(retry_settings)
    assert retry_handler.retries_exhausted(retry_settings)
