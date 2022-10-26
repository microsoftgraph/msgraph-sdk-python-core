# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TypeVar

import httpx
from kiota_abstractions.authentication import AccessTokenProvider
from kiota_http.middleware.middleware import BaseMiddleware

from .._enums import FeatureUsageFlag
from .middleware import GraphRequest


class GraphAuthorizationHandler(BaseMiddleware):
    """
    Transparently authorize requests by adding authorization header to the request
    """

    def __init__(self, token_provider: AccessTokenProvider):
        """Constructor for authorization handler

        Args:
            auth_provider (AuthenticationProvider): AuthorizationProvider instance
            that will be used to fetch the token
        """
        super().__init__()

        self.token_provider = token_provider

    async def send(
        self, request: GraphRequest, transport: httpx.AsyncBaseTransport
    ) -> httpx.Response:

        request.context.feature_usage = FeatureUsageFlag.AUTH_HANDLER_ENABLED

        token = await self.token_provider.get_authorization_token(str(request.url))
        request.headers.update({'Authorization': f'Bearer {token}'})
        response = await super().send(request, transport)
        return response
