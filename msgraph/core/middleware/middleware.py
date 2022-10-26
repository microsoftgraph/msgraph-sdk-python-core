# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

import httpx
from kiota_http.middleware import MiddlewarePipeline

from .request_context import GraphRequestContext


class GraphRequest(httpx.Request):
    """Http Request object with a custom request context
    """
    context: GraphRequestContext


class GraphMiddlewarePipeline(MiddlewarePipeline):
    """Chain of graph specific middleware that process requests in the same order
    and responses in reverse order to requests. The pipeline is implemented as a linked-list
    """

    async def send(self, request: GraphRequest) -> httpx.Response:
        """Passes the request to the next middleware if available or makes a network request

        Args:
            request (httpx.Request): The http request

        Returns:
            httpx.Response: The http response
        """

        request_options = {}
        options = request.headers.pop('request_options', None)
        if options:
            request_options = json.loads(options)

        request.context = GraphRequestContext(request_options, request.headers)

        if self._middleware_present():
            return await self._first_middleware.send(request, self._transport)
        # No middleware in pipeline, send the request.
        response = await self._transport.handle_async_request(request)
        response.request = request
        return response
