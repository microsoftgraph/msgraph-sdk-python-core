# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools

from requests import Session

from ._constants import DEFAULT_CONNECTION_TIMEOUT, DEFAULT_REQUEST_TIMEOUT
from ._enums import APIVersion, NationalClouds
from .middleware.abc_token_credential import TokenCredential
from .middleware.authorization import AuthorizationHandler
from .middleware.middleware import BaseMiddleware, MiddlewarePipeline
from .middleware.retry import RetryHandler
from .middleware.telemetry import TelemetryHandler


class HTTPClientFactory:
    """Constructs native HTTP Client(session) instances configured with either custom or default
    pipeline of middleware.

    :func: Class constructor accepts a user provided session object and kwargs to configure the
        request handling behaviour of the client
    :keyword enum api_version: The Microsoft Graph API version to be used, for example
        `APIVersion.v1` (default). This value is used in setting the base url for all requests for
        that session.
        :class:`~msgraphcore.enums.APIVersion` defines valid API versions.
    :keyword enum cloud: a supported Microsoft Graph cloud endpoint.
        Defaults to `NationalClouds.Global`
        :class:`~msgraphcore.enums.NationalClouds` defines supported sovereign clouds.
    :keyword tuple timeout: Default connection and read timeout values for all session requests.
        Specify a tuple in the form of Tuple(connect_timeout, read_timeout) if you would like to set
        the values separately. If you specify a single value for the timeout, the timeout value will
        be applied to both the connect and the read timeouts.
    :keyword obj session: A custom Session instance from the python requests library
    """
    def __init__(self, **kwargs):
        """Class constructor that accepts a user provided session object and kwargs
        to configure the request handling behaviour of the client"""
        self.api_version = kwargs.get('api_version', APIVersion.v1)
        self.endpoint = kwargs.get('cloud', NationalClouds.Global)
        self.timeout = kwargs.get('timeout', (DEFAULT_CONNECTION_TIMEOUT, DEFAULT_REQUEST_TIMEOUT))
        self.session = kwargs.get('session', Session())

        self._set_base_url()
        self._set_default_timeout()

    def create_with_default_middleware(self, credential: TokenCredential, **kwargs) -> Session:
        """Applies the default middleware chain to the HTTP Client

        :param credential: TokenCredential used to acquire an access token for the Microsoft
            Graph API. Created through one of the credential classes from `azure.identity`
        """
        middleware = [
            AuthorizationHandler(credential, **kwargs),
            RetryHandler(**kwargs),
            TelemetryHandler(),
        ]
        self._register(middleware)
        return self.session

    def create_with_custom_middleware(self, middleware: [BaseMiddleware]) -> Session:
        """Applies a custom middleware chain to the HTTP Client

        :param list middleware: Custom middleware(HTTPAdapter) list that will be used to create
            a middleware pipeline. The middleware should be arranged in the order in which they will
            modify the request.
        """
        if not middleware:
            raise ValueError("Please provide a list of custom middleware")
        self._register(middleware)
        return self.session

    def _set_base_url(self):
        """Helper method to set the base url"""
        base_url = self.endpoint + '/' + self.api_version
        self.session.base_url = base_url

    def _set_default_timeout(self):
        """Helper method to set a default timeout for the session
        Reference: https://github.com/psf/requests/issues/2011
        """
        self.session.request = functools.partial(self.session.request, timeout=self.timeout)

    def _register(self, middleware: [BaseMiddleware]) -> None:
        """
        Helper method that constructs a middleware_pipeline with the specified middleware
        """
        if middleware:
            middleware_pipeline = MiddlewarePipeline()
            for ware in middleware:
                middleware_pipeline.add_middleware(ware)

            self.session.mount('https://', middleware_pipeline)
