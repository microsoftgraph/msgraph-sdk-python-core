# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import annotations

from typing import List, Optional

import httpx
from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_http.middleware.middleware import BaseMiddleware

from ._enums import APIVersion, NationalClouds
from .middleware import AsyncGraphTransport, GraphTelemetryHandler


class GraphClientFactory(KiotaClientFactory):
    """Constructs httpx.AsyncClient instances configured with either custom or default
    pipeline of graph specific middleware.
    """

    @staticmethod
    def create_with_default_middleware(
        api_version: APIVersion = APIVersion.v1,
        host: NationalClouds = NationalClouds.Global
    ) -> httpx.AsyncClient:
        """Constructs native HTTP AsyncClient(httpx.AsyncClient) instances configured with
        a custom transport loaded with a default pipeline of middleware.
        Returns:
            httpx.AsycClient: An instance of the AsyncClient object
        """
        client = KiotaClientFactory.get_default_client()
        client.base_url = GraphClientFactory._get_base_url(host, api_version)
        current_transport = client._transport

        middleware = KiotaClientFactory.get_default_middleware()
        middleware.append(GraphTelemetryHandler())
        middleware_pipeline = KiotaClientFactory.create_middleware_pipeline(
            middleware, current_transport
        )

        client._transport = AsyncGraphTransport(
            transport=current_transport, pipeline=middleware_pipeline
        )
        client._transport.pipeline
        return client

    @staticmethod
    def create_with_custom_middleware(
        middleware: Optional[List[BaseMiddleware]],
        api_version: APIVersion = APIVersion.v1,
        host: NationalClouds = NationalClouds.Global,
    ) -> httpx.AsyncClient:
        """Applies a custom middleware chain to the HTTP Client

        Args:
            middleware(List[BaseMiddleware]): Custom middleware list that will be used to create
            a middleware pipeline. The middleware should be arranged in the order in which they will
            modify the request.
        """
        client = KiotaClientFactory.get_default_client()
        client.base_url = GraphClientFactory._get_base_url(host, api_version)
        current_transport = client._transport

        middleware_pipeline = KiotaClientFactory.create_middleware_pipeline(
            middleware, current_transport
        )

        client._transport = AsyncGraphTransport(
            transport=current_transport, pipeline=middleware_pipeline
        )
        return client

    @staticmethod
    def _get_base_url(host: str, api_version: APIVersion) -> str:
        """Helper method to set the complete base url"""
        base_url = f'{host}/{api_version}'
        return base_url
