import platform
import uuid

from msgraphcore.constants import BASE_URL, SDK_VERSION
from msgraphcore.middleware.middleware import BaseMiddleware


class TelemetryMiddleware(BaseMiddleware):
    def send(self, request, **kwargs):
        """Attaches metadata to a Graph request"""

        self._add_client_request_id_header(request)
        self._append_sdk_version_header(request)
        self._add_host_os_header(request)
        self._add_runtime_environment_header(request)

        response = super().send(request, **kwargs)
        return response

    def _add_client_request_id_header(self, request) -> None:
        """Add a client-request-id header with GUID value to request"""
        client_request_id = str(uuid.uuid4())
        request.headers.update({'client-request-id': '{}'.format(client_request_id)})

    def _append_sdk_version_header(self, request) -> None:
        """Add SdkVersion request header to each request to identify the language and
        version of the client SDK library(s).
        """
        if 'sdkVersion' in request.headers:
            request.headers.update(
                {
                    'sdkVersion':
                    'graph-python-core/' + SDK_VERSION + ', ' + request.headers.get('sdkVersion')
                }
            )
        else:
            request.headers.update({'sdkVersion': 'graph-python-core/' + SDK_VERSION})

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
