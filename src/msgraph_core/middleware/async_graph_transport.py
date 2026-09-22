import json

import httpx
from kiota_http.middleware import MiddlewarePipeline, RedirectHandler, RetryHandler

from .._enums import FeatureUsageFlag
from .request_context import GraphRequestContext

# Older supported Kiota releases do not export this request extension key.
REQUEST_OPTIONS_KEY = 'kiota_request_options'


class AsyncGraphTransport(httpx.AsyncBaseTransport):
    """A custom transport for requests to the Microsoft Graph API
    """

    def __init__(self, transport: httpx.AsyncBaseTransport, pipeline: MiddlewarePipeline) -> None:
        self.transport = transport
        self.pipeline = pipeline

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if self.pipeline and (
            REQUEST_OPTIONS_KEY in request.extensions or hasattr(request, 'options')
        ):
            self.set_request_context_and_feature_usage(request)
            response = await self.pipeline.send(request)
            return response

        response = await self.transport.handle_async_request(request)
        return response

    def set_request_context_and_feature_usage(self, request: httpx.Request) -> httpx.Request:

        request_options = request.extensions.get(REQUEST_OPTIONS_KEY)
        if request_options is None:
            request_options = request.options  # type:ignore

        context = GraphRequestContext(request_options, request.headers)
        middleware = self.pipeline._first_middleware
        while middleware:
            if isinstance(middleware, RedirectHandler):
                context.feature_usage = FeatureUsageFlag.REDIRECT_HANDLER_ENABLED
            if isinstance(middleware, RetryHandler):
                context.feature_usage = FeatureUsageFlag.RETRY_HANDLER_ENABLED

            middleware = middleware.next
        request.context = context  #type: ignore
        return request
