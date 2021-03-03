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
    assert retry_handler.total_retries == retry_handler.DEFAULT_TOTAL_RETRIES
    assert retry_handler.timeout == retry_handler.DEFAULT_RETRY_TIME_LIMIT
    assert retry_handler.backoff_max == retry_handler.MAXIMUM_BACKOFF
    assert retry_handler.backoff_factor == retry_handler.DEFAULT_BACKOFF_FACTOR
    assert retry_handler._allowed_methods == frozenset(
        ['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE']
    )
    assert retry_handler._respect_retry_after_header
    assert retry_handler._retry_on_status_codes == retry_handler._DEFAULT_RETRY_CODES


def test_custom_config():
    """
    Test that default configuration is overrriden if custom configuration is provided
    """
    retry_handler = RetryMiddleware(
        retry_configs={
            "retry_total": 10,
            "retry_backoff_factor": 0.2,
            "retry_backoff_max": 200,
            "retry_time_limit": 100,
            "retry_on_status_codes": [502, 503],
        }
    )

    assert retry_handler.total_retries == 10
    assert retry_handler.timeout == 100
    assert retry_handler.backoff_max == 200
    assert retry_handler.backoff_factor == 0.2
    assert retry_handler._retry_on_status_codes == {429, 502, 503, 504}


def test_disable_retries():
    """
    Test that when disable retries is called, total retries are set to zero
    """
    retry_handler = RetryMiddleware.disable_retries()
    assert retry_handler.total_retries == 0
    retry_settings = retry_handler.configure_retry_settings()
    assert not retry_handler.increment_counter(retry_settings)
    assert retry_handler.retries_exhausted(retry_settings)


def test_configure_settings_no_session_configs():
    """
    Test that settings are picked from the defaults if no configs are passed to the GraphSession
    """
    retry_handler = RetryMiddleware(retry_configs={})
    settings = retry_handler.configure_retry_settings()

    assert settings['total'] == retry_handler.DEFAULT_TOTAL_RETRIES
    assert settings['backoff'] == retry_handler.DEFAULT_BACKOFF_FACTOR
    assert settings['max_backoff'] == retry_handler.MAXIMUM_BACKOFF
    assert settings['timeout'] == retry_handler.DEFAULT_RETRY_TIME_LIMIT
    assert settings['retry_codes'] == retry_handler._retry_on_status_codes
    assert settings['methods'] == retry_handler._allowed_methods


def test_configure_settings_with_session_configs():
    """
    Test that settings are picked from configs passed to the GraphSession if provided
    """
    retry_handler = RetryMiddleware(
        retry_configs={
            'retry_total': 15,
            'retry_backoff_factor': 3,
            'retry_on_status_codes': [502, 503]
        }
    )
    settings = retry_handler.configure_retry_settings()

    assert settings['total'] == 15
    assert settings['backoff'] == 3
    assert settings['max_backoff'] == retry_handler.MAXIMUM_BACKOFF
    assert settings['timeout'] == retry_handler.DEFAULT_RETRY_TIME_LIMIT
    assert settings['retry_codes'] == retry_handler._retry_on_status_codes
    assert settings['methods'] == retry_handler._allowed_methods
