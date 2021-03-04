from email.utils import formatdate
from time import time

import pytest
import requests
import responses

from msgraphcore.constants import BASE_URL
from msgraphcore.graph_session import GraphSession
from msgraphcore.middleware.retry_middleware import RetryMiddleware


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


@responses.activate
def test_method_retryable_with_valid_method():
    """
    Test the is_method_retryable helper method with a valid HTTP response code
    """
    responses.add(responses.GET, BASE_URL, status=502)
    response = requests.get(BASE_URL)

    retry_handler = RetryMiddleware(retry_configs={})
    settings = retry_handler.configure_retry_settings()

    assert retry_handler._is_method_retryable(settings, response.request)


@responses.activate
def test_method_retryable_with_invalid_method():
    """
    Test the is_method_retryable helper method with an invalid HTTP response code
    """
    responses.add(responses.POST, BASE_URL, body="Test", status=503)
    response = requests.post(BASE_URL, data={"left": 1, "right": 3})

    retry_handler = RetryMiddleware(retry_configs={})
    settings = retry_handler.configure_retry_settings()

    assert not retry_handler._is_method_retryable(settings, response.request)


@responses.activate
def test_should_retry_valid():
    """
    Test the should_retry method with a valid HTTP method and response code
    """
    responses.add(responses.GET, BASE_URL, status=503)
    response = requests.get(BASE_URL)

    retry_handler = RetryMiddleware(retry_configs={})
    settings = retry_handler.configure_retry_settings()

    assert retry_handler.should_retry(settings, response)


@responses.activate
def test_should_retry_invalid():
    """
    Test the should_retry method with an valid HTTP response code
    """
    responses.add(responses.GET, BASE_URL, status=502)
    response = requests.get(BASE_URL)

    retry_handler = RetryMiddleware(retry_configs={})
    settings = retry_handler.configure_retry_settings()

    assert not retry_handler.should_retry(settings, response)


def test_retries_exhausted():
    """
    Test that the retries exhausted method works correctly when retries is greater than zero
    """
    retry_handler = RetryMiddleware(retry_configs={})
    settings = retry_handler.configure_retry_settings()

    assert not retry_handler.retries_exhausted(settings)


def test_retries_exhausted_zero_total():
    """
    Test that the retries exhausted method works correctly when total retries are set to zero
    """
    retry_handler = RetryMiddleware(retry_configs={'retry_total': 0})
    settings = retry_handler.configure_retry_settings()

    assert retry_handler.retries_exhausted(settings)


def test_increment_counter():
    """
    Test that retry counter is incremented on a valid retry
    """
    retry_handler = RetryMiddleware(retry_configs={})
    settings = retry_handler.configure_retry_settings()

    assert retry_handler.increment_counter(settings)
    assert settings['total'] == retry_handler.DEFAULT_TOTAL_RETRIES - 1


def test_increment_counter_invalid_retry():
    """
    Test that retry counter is not incremented when a retry is not valid
    """
    retry_handler = RetryMiddleware(retry_configs={'retry_total': 0})
    settings = retry_handler.configure_retry_settings()

    assert not retry_handler.increment_counter(settings)
    assert settings['total'] == 0


@responses.activate
def test_get_retry_after():
    """
    Test the _get_retry_after method with an integer value for retry header.
    """
    responses.add(responses.GET, BASE_URL, headers={'Retry-After': "120"}, status=503)
    response = requests.get(BASE_URL)

    retry_handler = RetryMiddleware(retry_configs={})

    assert retry_handler._get_retry_after(response) == 120


@responses.activate
def test_get_retry_after_no_header():
    """
    Test the _get_retry_after method with no Retry-After header.
    """
    responses.add(responses.GET, BASE_URL, status=503)
    response = requests.get(BASE_URL)

    retry_handler = RetryMiddleware(retry_configs={})

    assert retry_handler._get_retry_after(response) is None


@responses.activate
def test_get_retry_after_http_date():
    """
    Test the _get_retry_after method with a http date as Retry-After value.
    """
    timevalue = time() + 120
    http_date = formatdate(timeval=timevalue, localtime=False, usegmt=True)
    responses.add(responses.GET, BASE_URL, headers={'Retry-After': f'{http_date}'}, status=503)
    response = requests.get(BASE_URL)

    retry_handler = RetryMiddleware(retry_configs={})

    assert retry_handler._get_retry_after(response) < 120
