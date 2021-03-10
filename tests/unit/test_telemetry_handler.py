import platform
import re
import uuid

import pytest
import requests
import responses

from msgraphcore.constants import BASE_URL, SDK_VERSION
from msgraphcore.graph_session import GraphSession
from msgraphcore.middleware.telemetry import TelemetryMiddleware


@responses.activate
def test_add_client_request_id_header():
    """
    Test that client_request_id is added to the request headers
    """
    responses.add(responses.GET, BASE_URL)
    response = requests.get(BASE_URL)
    request = response.request

    telemetry_handler = TelemetryMiddleware()
    telemetry_handler._add_client_request_id_header(request)

    assert 'client-request-id' in request.headers
    assert _is_valid_uuid(request.headers.get('client-request-id'))


@responses.activate
def test_append_sdk_version_header():
    """
    Test that sdkVersion is added to the request headers
    """
    responses.add(responses.GET, BASE_URL)
    response = requests.get(BASE_URL)
    request = response.request

    telemetry_handler = TelemetryMiddleware()
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

    telemetry_handler = TelemetryMiddleware()
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

    telemetry_handler = TelemetryMiddleware()
    telemetry_handler._add_runtime_environment_header(request)

    assert 'RuntimeEnvironment' in request.headers
    assert request.headers.get('RuntimeEnvironment') == runtime_environment


def _is_valid_uuid(guid):
    regex = "^[{]?[0-9a-fA-F]{8}" + "-([0-9a-fA-F]{4}-)" + "{3}[0-9a-fA-F]{12}[}]?$"
    pattern = re.compile(regex)
    if re.search(pattern, guid):
        return True
    return False
