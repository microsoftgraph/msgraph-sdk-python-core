import typing
from http import client

import httpx
from kiota_http.middleware import BaseMiddleware, RedirectHandler

from .._enums import FeatureUsageFlag
from .middleware import GraphRequest


class GraphRedirectHandler(RedirectHandler):
    """Middleware designed to handle 3XX responses transparently
    """

    async def send(
        self, request: GraphRequest, transport: httpx.AsyncBaseTransport
    ) -> httpx.Response:
        """Sends the http request object to the next middleware or redirects
        the request if necessary.
        """
        request.context.feature_usage = FeatureUsageFlag.REDIRECT_HANDLER_ENABLED

        retryable = True
        while retryable:
            response = await super(RedirectHandler, self).send(request, transport)
            redirect_location = self.get_redirect_location(response)
            if redirect_location and self.should_redirect:
                retryable = self.increment(response)
                request = self._build_redirect_request(request, response)
                continue

            response.history = self.history
            return response

        raise Exception(f"Too many redirects. {response.history}")
