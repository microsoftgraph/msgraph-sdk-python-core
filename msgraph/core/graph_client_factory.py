# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import httpx
from kiota_abstractions.authentication import AuthenticationProvider
from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_http.middleware import AsyncKiotaTransport

from ._constants import DEFAULT_CONNECTION_TIMEOUT, DEFAULT_REQUEST_TIMEOUT
from ._enums import APIVersion, NationalClouds
from .middleware import AuthorizationHandler, GraphMiddlewarePipeline, TelemetryHandler


class GraphClientFactory(KiotaClientFactory):
    """Constructs httpx AsyncClient instances configured with either custom or default
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

    def __init__(
        self,
        api_version: APIVersion,
        endpoint: NationalClouds,
        timeout: httpx.Timeout,
        client: httpx.AsyncClient,
    ):
        """Class constructor that accepts a user provided session object and kwargs
        to configure the request handling behaviour of the client"""
        self.api_version = api_version
        self.endpoint = endpoint
        self.timeout = timeout
        self.client = client

    def create_with_default_middleware(
        self, auth_provider: AuthenticationProvider
    ) -> httpx.AsyncClient:
        """Constructs native HTTP AsyncClient(httpx.AsyncClient) instances configured with
        a custom transport loaded with a default pipeline of middleware.
        Returns:
            httpx.AsycClient: An instance of the AsyncClient object
        """
        graph_async_client = httpx.AsyncClient(
            base_url=self._get_base_url(), timeout=self.timeout, http2=True
        )
        current_transport = graph_async_client._transport
        middleware = self._get_default_middleware(auth_provider, current_transport)

        graph_async_client._transport = AsyncKiotaTransport(
            transport=current_transport, middleware=middleware
        )
        return graph_async_client

    # def create_with_custom_middleware(self,
    #                                   middleware: [BaseMiddleware]) -> Session:
    #     """Applies a custom middleware chain to the HTTP Client

    #     :param list middleware: Custom middleware(HTTPAdapter) list that will be used to create
    #         a middleware pipeline. The middleware should be arranged in the order in which they will
    #         modify the request.
    #     """
    #     if not middleware:
    #         raise ValueError("Please provide a list of custom middleware")
    #     self._register(middleware)
    #     return self.session

    def _get_base_url(self):
        """Helper method to set the base url"""
        base_url = self.endpoint + '/' + self.api_version
        return base_url

    # def _get_default_timeout(self):
    #     """Helper method to set a default timeout for the session
    #     Reference: https://github.com/psf/requests/issues/2011
    #     """
    #     self.session.request = functools.partial(self.session.request,
    #                                              timeout=self.timeout)

    def _get_default_middleware(
        self, auth_provider: AuthenticationProvider, transport: httpx.AsyncBaseTransport
    ) -> GraphMiddlewarePipeline:
        """
        Helper method that constructs a middleware_pipeline with the specified middleware
        """
        middleware_pipeline = GraphMiddlewarePipeline(transport)
        middleware = [AuthorizationHandler(auth_provider), TelemetryHandler()]
        for ware in middleware:
            middleware_pipeline.add_middleware(ware)

        return middleware_pipeline