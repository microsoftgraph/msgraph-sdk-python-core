from ._base_auth import AuthProviderBase
from .options.constants import AUTH_MIDDLEWARE_OPTIONS
from ._middleware import Middleware


class AuthorizationHandler(Middleware):
    def __init__(self, auth_provider: AuthProviderBase, auth_provider_options=None):
        super().__init__()
        self.auth_provider = auth_provider
        self.auth_provider_options = auth_provider_options

    def send(self, request, **kwargs):
        options = self._get_middleware_options(request)

        if options:
            self.auth_provider.scopes = options.scopes

        token = self.auth_provider.get_access_token()
        request.headers.update({'Authorization': 'Bearer {}'.format(token)})

        return super().send(request, **kwargs)

    def _get_middleware_options(self, request):
        return request.middleware_control.get(AUTH_MIDDLEWARE_OPTIONS) or self.auth_provider_options
