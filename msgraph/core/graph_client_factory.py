# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import List, Optional

import httpx
from kiota_abstractions.authentication import AccessTokenProvider
from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_http.middleware import AsyncKiotaTransport
from kiota_http.middleware.middleware import BaseMiddleware

from ._constants import DEFAULT_CONNECTION_TIMEOUT, DEFAULT_REQUEST_TIMEOUT
from ._enums import APIVersion, NationalClouds
from .middleware import (
    GraphAuthorizationHandler,
    GraphMiddlewarePipeline,
    GraphRedirectHandler,
    GraphRetryHandler,
    GraphTelemetryHandler,
)


class GraphClientFactory(KiotaClientFactory):
    """Constructs httpx.AsyncClient instances configured with either custom or default
    pipeline of graph specific middleware.
    """

    def __init__(
        self,
        api_version: APIVersion,
        base_url: NationalClouds,
        timeout: httpx.Timeout,
        client: Optional[httpx.AsyncClient],
    ):
        """Class constructor accepts a user provided client object and kwargs to configure the
        request handling behaviour of the client

        Args:
            api_version (APIVersion): The Microsoft Graph API version to be used, for example
                                    `APIVersion.v1` (default). This value is used in setting
                                    the base url for all requests for that session.
            base_url (NationalClouds): a supported Microsoft Graph cloud endpoint.
            timeout (httpx.Timeout):Default connection and read timeout values for all session
                                    requests.Specify a tuple in the form of httpx.Timeout(
                                    REQUEST_TIMEOUT, connect=CONNECTION_TIMEOUT),
            client (Optional[httpx.AsyncClient]): A custom AsynClient instance from the
                                    python httpx library
        """
        self.api_version = api_version
        self.base_url = base_url
        self.timeout = timeout
        self.client = client

    def create_with_default_middleware(
        self, token_provider: AccessTokenProvider
    ) -> httpx.AsyncClient:
        """Constructs native HTTP AsyncClient(httpx.AsyncClient) instances configured with
        a custom transport loaded with a default pipeline of middleware.
        Returns:
            httpx.AsycClient: An instance of the AsyncClient object
        """
        if not self.client:
            self.client = httpx.AsyncClient(
                base_url=self._get_base_url(), timeout=self.timeout, http2=True
            )
        current_transport = self.client._transport
        middleware = self._get_default_middleware(token_provider, current_transport)

        self.client._transport = AsyncKiotaTransport(
            transport=current_transport, middleware=middleware
        )
        return self.client

    def create_with_custom_middleware(
        self, middleware: Optional[List[BaseMiddleware]]
    ) -> httpx.AsyncClient:
        """Applies a custom middleware chain to the HTTP Client

        Args:
            middleware(List[BaseMiddleware]): Custom middleware list that will be used to create
            a middleware pipeline. The middleware should be arranged in the order in which they will
            modify the request.
        """
        if not self.client:
            self.client = httpx.AsyncClient(
                base_url=self._get_base_url(), timeout=self.timeout, http2=True
            )
        current_transport = self.client._transport

        self.client._transport = AsyncKiotaTransport(
            transport=current_transport, middleware=middleware
        )
        return self.client

    def _get_base_url(self):
        """Helper method to set the base url"""
        base_url = self.base_url + '/' + self.api_version
        return base_url

    def _get_default_middleware(
        self, token_provider: AccessTokenProvider, transport: httpx.AsyncBaseTransport
    ) -> GraphMiddlewarePipeline:
        """
        Helper method that constructs a middleware_pipeline with the specified middleware
        """
        middleware_pipeline = GraphMiddlewarePipeline(transport)
        middleware = [
            GraphAuthorizationHandler(token_provider),
            GraphRedirectHandler(),
            GraphRetryHandler(),
            GraphTelemetryHandler()
        ]
        for ware in middleware:
            middleware_pipeline.add_middleware(ware)

        return middleware_pipeline
