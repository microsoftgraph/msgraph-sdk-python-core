from email.utils import formatdate
from time import time

import pytest
import requests
import responses

from msgraph.core import APIVersion, NationalClouds
from msgraph.core.middleware.retry import RetryHandler

BASE_URL = NationalClouds.Global + '/' + APIVersion.v1


def test_no_config():
    """
    Test that default values are used if no custom confguration is passed
    """
    retry_handler = RetryHandler()
    assert retry_handler.max_retries == retry_handler.DEFAULT_MAX_RETRIES
    assert retry_handler.timeout == retry_handler.MAX_DELAY
    assert retry_handler.backoff_max == retry_handler.MAXIMUM_BACKOFF
    assert retry_handler.backoff_factor == retry_handler.DEFAULT_BACKOFF_FACTOR
    assert retry_handler._allowed_methods == frozenset(
        ['HEAD', 'GET', 'PUT', 'POST', 'PATCH', 'DELETE', 'OPTIONS']
    )
    assert retry_handler._respect_retry_after_header
    assert retry_handler._retry_on_status_codes == retry_handler._DEFAULT_RETRY_STATUS_CODES


def test_custom_config():
    """
    Test that default configuration is overrriden if custom configuration is provided
    """
    retry_handler = RetryHandler(
        max_retries=10,
        retry_backoff_factor=0.2,
        retry_backoff_max=200,
        retry_time_limit=100,
        retry_on_status_codes=[502, 503]
    )

    assert retry_handler.max_retries == 10
    assert retry_handler.timeout == 100
    assert retry_handler.backoff_max == 200
    assert retry_handler.backoff_factor == 0.2
    assert retry_handler._retry_on_status_codes == {429, 502, 503, 504}


def test_disable_retries():
    """
    Test that when disable_retries class method is called, total retries are set to zero
    """
    retry_handler = RetryHandler()
    retry_handler = retry_handler.disable_retries()
    assert retry_handler.max_retries == 0
    retry_options = retry_handler.get_retry_options({})
    assert not retry_handler.check_retry_valid(retry_options, 0)


@responses.activate
def test_method_retryable_with_valid_method():
    """
    Test if method is retryable with a retryable request method.
    """
    responses.add(responses.GET, BASE_URL, status=502)
    response = requests.get(BASE_URL)

    retry_handler = RetryHandler()
    settings = retry_handler.get_retry_options({})

    assert retry_handler._is_method_retryable(settings, response.request)


@responses.activate
def test_should_retry_valid():
    """
    Test the should_retry method with a valid HTTP method and response code
    """
    responses.add(responses.GET, BASE_URL, status=503)
    response = requests.get(BASE_URL)

    retry_handler = RetryHandler()
    settings = retry_handler.get_retry_options({})

    assert retry_handler.should_retry(settings, response)


@responses.activate
def test_should_retry_invalid():
    """
    Test the should_retry method with an valid HTTP response code
    """
    responses.add(responses.GET, BASE_URL, status=502)
    response = requests.get(BASE_URL)

    retry_handler = RetryHandler()
    settings = retry_handler.get_retry_options({})

    assert not retry_handler.should_retry(settings, response)


@responses.activate
def test_is_request_payload_buffered_valid():
    """
    Test for _is_request_payload_buffered helper method.
    Should return true request payload is buffered/rewindable.
    """
    responses.add(responses.GET, BASE_URL, status=429)
    response = requests.get(BASE_URL)

    retry_handler = RetryHandler()

    assert retry_handler._is_request_payload_buffered(response)


@responses.activate
def test_is_request_payload_buffered_invalid():
    """
    Test for _is_request_payload_buffered helper method.
    Should return false if request payload is forward streamed.
    """
    responses.add(responses.POST, BASE_URL, status=429)
    response = requests.post(BASE_URL, headers={'Content-Type': "application/octet-stream"})

    retry_handler = RetryHandler()

    assert not retry_handler._is_request_payload_buffered(response)


def test_check_retry_valid():
    """
    Test that a retry is valid if the maximum number of retries has not been reached
    """
    retry_handler = RetryHandler()
    settings = retry_handler.get_retry_options({})

    assert retry_handler.check_retry_valid(settings, 0)


def test_check_retry_valid_no_retries():
    """
    Test that a retry is not valid if maximum number of retries has been reached
    """
    retry_handler = RetryHandler(max_retries=2)
    settings = retry_handler.get_retry_options({})

    assert not retry_handler.check_retry_valid(settings, 2)


@responses.activate
def test_get_retry_after():
    """
    Test the _get_retry_after method with an integer value for retry header.
    """
    responses.add(responses.GET, BASE_URL, headers={'Retry-After': "120"}, status=503)
    response = requests.get(BASE_URL)

    retry_handler = RetryHandler()

    assert retry_handler._get_retry_after(response) == 120


@responses.activate
def test_get_retry_after_no_header():
    """
    Test the _get_retry_after method with no Retry-After header.
    """
    responses.add(responses.GET, BASE_URL, status=503)
    response = requests.get(BASE_URL)

    retry_handler = RetryHandler()

    assert retry_handler._get_retry_after(response) is None


@responses.activate
def test_get_retry_after_http_date():
    """
    Test the _get_retry_after method with a http date as Retry-After value.
    """
    timevalue = time() + 120
    http_date = formatdate(timeval=timevalue, localtime=False, usegmt=True)
    responses.add(responses.GET, BASE_URL, headers={'retry-after': f'{http_date}'}, status=503)
    response = requests.get(BASE_URL)

    retry_handler = RetryHandler()

    assert retry_handler._get_retry_after(response) < 120
