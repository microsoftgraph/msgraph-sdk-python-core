import http
import json
import platform

import httpx
from kiota_http.middleware import BaseMiddleware
from urllib3.util import parse_url

from .._constants import SDK_VERSION
from .._enums import APIVersion, NationalClouds
from .async_graph_transport import AsyncGraphTransport
from .options import GraphTelemetryHandlerOption
from .request_context import GraphRequestContext


class GraphRequest(httpx.Request):
    context: GraphRequestContext


class GraphTelemetryHandler(BaseMiddleware):
    """Middleware component that attaches metadata to a Graph request in order to help
    the SDK team improve the developer experience.
    """

    def __init__(
        self, options: GraphTelemetryHandlerOption = GraphTelemetryHandlerOption(), **kwargs
    ):
        """Create an instance of GraphTelemetryHandler

        Args:
            options (GraphTelemetryHandlerOption, optional): The graph telemetry handler
            options value. Defaults to GraphTelemetryHandlerOption
        """
        super().__init__()
        self.options = options

    async def send(self, request: GraphRequest, transport: AsyncGraphTransport):
        """Adds telemetry headers and sends the http request.
        """

        if self.is_graph_url(request.url):
            self._add_client_request_id_header(request)
            self._append_sdk_version_header(request)
            self._add_host_os_header(request)
            self._add_runtime_environment_header(request)

        response = await super().send(request, transport)
        return response

    def is_graph_url(self, url):
        """Check if the request is made to a graph endpoint. We do not add telemetry headers to
        non-graph endpoints"""
        endpoints = set(item.value for item in NationalClouds)

        base_url = parse_url(str(url))
        endpoint = f"{base_url.scheme}://{base_url.netloc}"
        return endpoint in endpoints

    def _add_client_request_id_header(self, request) -> None:
        """Add a client-request-id header with GUID value to request"""
        request.headers.update({'client-request-id': f'{request.context.client_request_id}'})

    def _append_sdk_version_header(self, request) -> None:
        """Add SdkVersion request header to each request to identify the language and
        version of the client SDK library(s).
        Also adds the featureUsage value.
        """
        sdk_name = 'graph-python-core'

        if self.options.api_version == APIVersion.v1:
            sdk_name = 'graph-python'
        if self.options.api_version == APIVersion.beta:
            sdk_name = 'graph-python-beta'

        if 'sdkVersion' in request.headers:
            sdk_version = request.headers.get('sdkVersion')
            if not sdk_version == f'{sdk_name}/{SDK_VERSION} '\
                f'(featureUsage={request.context.feature_usage})':
                request.headers.update(
                    {
                        'sdkVersion':
                        f'{sdk_name}/{SDK_VERSION},{ sdk_version} '\
                        f'(featureUsage={request.context.feature_usage})'
                    }
                )
        else:
            request.headers.update(
                {
                    'sdkVersion':
                    f'{sdk_name}/{SDK_VERSION} '\
                    f'(featureUsage={request.context.feature_usage})'
                }
            )

    def _add_host_os_header(self, request) -> None:
        """
        Add HostOS request header to each request to help identify the OS
        on which our client SDK is running on
        """
        system = platform.system()
        version = platform.version()
        host_os = f'{system} {version}'
        request.headers.update({'HostOs': host_os})

    def _add_runtime_environment_header(self, request) -> None:
        """
        Add RuntimeEnvironment request header to capture the runtime framework
         on which the client SDK is running on.
        """
        python_version = platform.python_version()
        runtime_environment = f'Python/{python_version}'
        request.headers.update({'RuntimeEnvironment': runtime_environment})
