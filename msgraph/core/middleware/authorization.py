# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from .._enums import FeatureUsageFlag
from .abc_token_credential import TokenCredential
from .middleware import BaseMiddleware


class AuthorizationHandler(BaseMiddleware):
    def __init__(self, credential: TokenCredential, **kwargs):
        super().__init__()
        self.credential = credential
        self.scopes = kwargs.get("scopes", ['.default'])
        self.retry_count = 0

    def send(self, request, **kwargs):
        context = request.context
        request.headers.update(
            {'Authorization': 'Bearer {}'.format(self._get_access_token(context))}
        )
        context.set_feature_usage = FeatureUsageFlag.AUTH_HANDLER_ENABLED
        response = super().send(request, **kwargs)

        # Token might have expired just before transmission, retry the request one more time
        if response.status_code == 401 and self.retry_count < 2:
            self.retry_count += 1
            return self.send(request, **kwargs)
        return response

    def _get_access_token(self, context):
        return self.credential.get_token(*self.get_scopes(context))[0]

    def get_scopes(self, context):
        # Checks if there are any options for this middleware
        return context.middleware_control.get('scopes', self.scopes)
