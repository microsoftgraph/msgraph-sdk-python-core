# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import annotations

from typing import List, Optional

import httpx
from kiota_abstractions.authentication import AccessTokenProvider
from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_http.middleware import AsyncKiotaTransport
from kiota_http.middleware.middleware import BaseMiddleware

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

    @staticmethod
    def create_with_default_middleware(
        client: httpx.AsyncClient,
        token_provider: Optional[AccessTokenProvider] = None
    ) -> httpx.AsyncClient:
        """Constructs native HTTP AsyncClient(httpx.AsyncClient) instances configured with
        a custom transport loaded with a default pipeline of middleware.
        Returns:
            httpx.AsycClient: An instance of the AsyncClient object
        """
        current_transport = client._transport
        middleware = GraphClientFactory._get_common_middleware()
        if token_provider:
            middleware.insert(0, GraphAuthorizationHandler(token_provider))

        middleware_pipeline = GraphClientFactory._create_middleware_pipeline(
            middleware, current_transport
        )

        client._transport = AsyncKiotaTransport(
            transport=current_transport, middleware=middleware_pipeline
        )
        return client

    @staticmethod
    def create_with_custom_middleware(
        client: httpx.AsyncClient, middleware: Optional[List[BaseMiddleware]]
    ) -> httpx.AsyncClient:
        """Applies a custom middleware chain to the HTTP Client

        Args:
            middleware(List[BaseMiddleware]): Custom middleware list that will be used to create
            a middleware pipeline. The middleware should be arranged in the order in which they will
            modify the request.
        """
        current_transport = client._transport
        middleware_pipeline = GraphClientFactory._create_middleware_pipeline(
            middleware, current_transport
        )

        client._transport = AsyncKiotaTransport(
            transport=current_transport, middleware=middleware_pipeline
        )
        return client

    @staticmethod
    def _get_common_middleware() -> List[BaseMiddleware]:
        """
        Helper method that returns a list of cross cutting middleware
        """
        middleware = [GraphRedirectHandler(), GraphRetryHandler(), GraphTelemetryHandler()]

        return middleware

    @staticmethod
    def _create_middleware_pipeline(
        middleware: Optional[List[BaseMiddleware]], transport: httpx.AsyncBaseTransport
    ) -> GraphMiddlewarePipeline:
        """
        Helper method that constructs a middleware_pipeline with the specified middleware
        """
        middleware_pipeline = GraphMiddlewarePipeline(transport)
        if middleware:
            for ware in middleware:
                middleware_pipeline.add_middleware(ware)
        return middleware_pipeline
