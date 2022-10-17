# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import httpx
from kiota_abstractions.authentication import AuthenticationProvider
from kiota_http.middleware.middleware import BaseMiddleware

from .._enums import FeatureUsageFlag


class AuthorizationHandler(BaseMiddleware):

    def __init__(self, auth_provider: AuthenticationProvider):
        super().__init__()
        self.auth_provider = auth_provider

    async def send(
        self, request: httpx.Request, transport: httpx.AsyncBaseTransport
    ) -> httpx.Response:
        context = request.context
        token = await self.auth_provider.get_authorization_token(str(request.url))
        request.headers.update({'Authorization': f'Bearer {token}'})
        context.set_feature_usage = FeatureUsageFlag.AUTH_HANDLER_ENABLED
        response = await super().send(request, transport)
        return response
