# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json

from kiota_http.middleware import MiddlewarePipeline

from .request_context import RequestContext


class GraphMiddlewarePipeline(MiddlewarePipeline):
    """Entry point of graph specific middleware
    The pipeline is implemented as a linked-list
    """

    async def send(self, request):

        middleware_control_string = request.headers.pop('middleware_control', None)
        if middleware_control_string:
            middleware_control = json.loads(middleware_control_string)
        else:
            middleware_control = dict()

        request.context = RequestContext(middleware_control, request.headers)

        if self._middleware_present():
            return await self._first_middleware.send(request, self._transport)
        # No middleware in pipeline, delete request optoions from header and
        # send the request
        del request.headers['request_options']
        return await self._transport.handle_async_request(request)
