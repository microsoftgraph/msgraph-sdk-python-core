import pytest

from msgraphcore.middleware.retry_middleware import RetryMiddleware


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
