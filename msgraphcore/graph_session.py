"""
Graph Session
"""
import logging
import os
import sys

from requests import Session

from msgraphcore.constants import BASE_URL, SDK_VERSION
from msgraphcore.middleware.abc_token_credential import TokenCredential
from msgraphcore.middleware.authorization import AuthorizationHandler
from msgraphcore.middleware.logger import HttpFormatter, log_roundtrip
from msgraphcore.middleware.middleware import BaseMiddleware, MiddlewarePipeline
from msgraphcore.middleware.options.middleware_control import middleware_control
from msgraphcore.middleware.retry_middleware import RetryMiddleware
from msgraphcore.middleware.telemetry import TelemetryMiddleware


class GraphSession(Session):
    """Extends Session with Graph functionality

    Extends Session by adding support for middleware options and middleware pipeline
    """
    def __init__(
        self,
        credential: TokenCredential,
        scopes: [str] = ['.default'],
        retry_config: dict = {},
        middleware: list = [],
        api_version: str = 'v1.0'
    ):
        super().__init__()
        self._base_url = BASE_URL + '/' + api_version

        auth_handler = AuthorizationHandler(credential, scopes)
        retry_handler = RetryMiddleware(retry_config)
        telemetry_handler = TelemetryMiddleware()

        # The authorization handler should be the first middleware in the pipeline.
        middleware.insert(0, auth_handler)
        middleware.insert(1, retry_handler)
        middleware.insert(2, telemetry_handler)
        self._register(middleware)

        if os.getenv("ENABLE_LOGGING", False):
            formatter = HttpFormatter('{asctime} {levelname} {name} {message}', style='{')
            root = logging.getLogger('graph_logger')
            if os.getenv("LOG_TO_FILE", True):
                file_handler = logging.FileHandler('graphsession.log')
                file_handler.setFormatter(formatter)
                root.addHandler(file_handler)
            if os.getenv("LOG_TO_CONSOLE", True):
                stream_handler = logging.StreamHandler(sys.stdout)
                stream_handler.setFormatter(formatter)
                root.addHandler(stream_handler)

            root.setLevel(logging.DEBUG)
            self.hooks['response'].append(log_roundtrip)

    @middleware_control.get_middleware_options
    def get(self, url: str, **kwargs):
        r"""Sends a GET request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return super().get(self._graph_url(url), **kwargs)

    @middleware_control.get_middleware_options
    def post(self, url, data=None, json=None, **kwargs):
        r"""Sends a POST request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return super().post(self._graph_url(url), data, json, **kwargs)

    @middleware_control.get_middleware_options
    def put(self, url, data=None, **kwargs):
        r"""Sends a PUT request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return super().put(self._graph_url(url), data, **kwargs)

    @middleware_control.get_middleware_options
    def patch(self, url, data=None, **kwargs):
        r"""Sends a PATCH request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return super().patch(self._graph_url(url), data, **kwargs)

    @middleware_control.get_middleware_options
    def delete(self, url, **kwargs):
        r"""Sends a DELETE request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \*\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        """
        return super().delete(self._graph_url(url), **kwargs)

    def _graph_url(self, url: str) -> str:
        """Appends BASE_URL to user provided path

        :param url: user provided path
        :return: graph_url
        """
        return self._base_url + url if (url[0] == '/') else url

    def _register(self, middleware: [BaseMiddleware]) -> None:
        """Adds middleware to middleware_pipeline

        :param middleware: list of middleware
        """
        if middleware:
            middleware_pipeline = MiddlewarePipeline()

            for ware in middleware:
                middleware_pipeline.add_middleware(ware)

            self.mount('https://', middleware_pipeline)
