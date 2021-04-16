import functools
from typing import Optional

from requests import Session

from msgraphcore.constants import CONNECTION_TIMEOUT, REQUEST_TIMEOUT
from msgraphcore.enums import APIVersion, NationalClouds
from msgraphcore.middleware.abc_token_credential import TokenCredential
from msgraphcore.middleware.authorization import AuthorizationHandler
from msgraphcore.middleware.middleware import BaseMiddleware, MiddlewarePipeline


class HTTPClientFactory:
    """
    Constructs HTTP Client(session) instances configured with either custom or default
    pipeline of middleware.
    """
    def __init__(self, session: Optional[Session], **kwargs):
        """Class constructor that accepts a user provided session object and kwargs
        to configure the request handling behaviour of the client"""
        self.api_version = kwargs.get("api_version", APIVersion.v1)
        self.endpoint = kwargs.get('cloud', NationalClouds.Global)
        self.timeout = kwargs.get('timeout', (CONNECTION_TIMEOUT, REQUEST_TIMEOUT))
        self.base_url = self._get_base_url()
        if session:
            self.session = session
        else:
            self.session = Session()
            self._set_default_timeout()

    # should this be a class method
    def create_with_default_middleware(self, credential: TokenCredential, **kwargs) -> Session:
        """Applies the default middleware chain to the HTTP Client"""
        middleware = [
            AuthorizationHandler(credential, **kwargs),
        ]
        self._register(middleware)
        return self.session

    def create_with_custom_middleware(self, middleware: [BaseMiddleware]) -> Session:
        """Applies a custom middleware chain to the HTTP Client """
        if not middleware:
            raise ValueError("Please provide a list of custom middleware")
        self._register(middleware)
        return self.session

    def _get_base_url(self):
        """Helper method to get the base url"""
        return self.endpoint + '/' + self.api_version

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
