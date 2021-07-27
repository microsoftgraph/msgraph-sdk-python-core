# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import platform
import re
import uuid

import pytest
import requests
import responses

from msgraph.core import SDK_VERSION, APIVersion, GraphClient, NationalClouds
from msgraph.core.middleware.request_context import RequestContext
from msgraph.core.middleware.telemetry import TelemetryHandler

BASE_URL = NationalClouds.Global + '/' + APIVersion.v1


@responses.activate
def test_is_graph_url():
    """
    Test method that checks whether a request url is a graph endpoint
    """
    responses.add(responses.GET, BASE_URL)
    response = requests.get(BASE_URL)
    request = response.request

    telemetry_handler = TelemetryHandler()
    assert telemetry_handler.is_graph_url(request.url)


@responses.activate
def test_is_not_graph_url():
    """
    Test method that checks whether a request url is a graph endpoint with a
    non-graph url
    """
    responses.add(responses.GET, 'https://httpbin.org/status/200')
    response = requests.get('https://httpbin.org/status/200')
    request = response.request

    telemetry_handler = TelemetryHandler()
    assert not telemetry_handler.is_graph_url(request.url)


@responses.activate
def test_add_client_request_id_header():
    """
    Test that client_request_id is added to the request headers
    """
    responses.add(responses.GET, BASE_URL)
    response = requests.get(BASE_URL)
    request = response.request
    request.context = RequestContext({}, {})

    telemetry_handler = TelemetryHandler()
    telemetry_handler._add_client_request_id_header(request)

    assert 'client-request-id' in request.headers
    assert _is_valid_uuid(request.headers.get('client-request-id'))


@responses.activate
def test_custom_client_request_id_header():
    """
    Test that a custom client request id is used, if provided
    """
    custom_id = str(uuid.uuid4())
    responses.add(responses.GET, BASE_URL)
    response = requests.get(BASE_URL)
    request = response.request
    request.context = RequestContext({}, {'client-request-id': custom_id})

    telemetry_handler = TelemetryHandler()
    telemetry_handler._add_client_request_id_header(request)

    assert 'client-request-id' in request.headers
    assert _is_valid_uuid(request.headers.get('client-request-id'))
    assert request.headers.get('client-request-id') == custom_id


@responses.activate
def test_append_sdk_version_header():
    """
    Test that sdkVersion is added to the request headers
    """
    responses.add(responses.GET, BASE_URL)
    response = requests.get(BASE_URL)
    request = response.request
    request.context = RequestContext({}, {})

    telemetry_handler = TelemetryHandler()
    telemetry_handler._append_sdk_version_header(request)

    assert 'sdkVersion' in request.headers
    assert request.headers.get('sdkVersion').startswith('graph-python-core/' + SDK_VERSION)


@responses.activate
def test_add_host_os_header():
    """
    Test that HostOs is added to the request headers
    """
    system = platform.system()
    version = platform.version()
    host_os = f'{system} {version}'

    responses.add(responses.GET, BASE_URL)
    response = requests.get(BASE_URL)
    request = response.request
    request.context = RequestContext({}, {})

    telemetry_handler = TelemetryHandler()
    telemetry_handler._add_host_os_header(request)

    assert 'HostOs' in request.headers
    assert request.headers.get('HostOs') == host_os


@responses.activate
def test_add_runtime_environment_header():
    """
    Test that RuntimeEnvironment is added to the request headers
    """
    python_version = platform.python_version()
    runtime_environment = f'Python/{python_version}'

    responses.add(responses.GET, BASE_URL)
    response = requests.get(BASE_URL)
    request = response.request
    request.context = RequestContext({}, {})

    telemetry_handler = TelemetryHandler()
    telemetry_handler._add_runtime_environment_header(request)

    assert 'RuntimeEnvironment' in request.headers
    assert request.headers.get('RuntimeEnvironment') == runtime_environment


def _is_valid_uuid(guid):
    regex = "^[{]?[0-9a-fA-F]{8}" + "-([0-9a-fA-F]{4}-)" + "{3}[0-9a-fA-F]{12}[}]?$"
    pattern = re.compile(regex)
    if re.search(pattern, guid):
        return True
    return False
