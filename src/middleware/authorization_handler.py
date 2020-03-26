from requests.adapters import HTTPAdapter

from ._base import AuthProviderBase
from .options.constants import AUTH_MIDDLEWARE_OPTIONS


class AuthorizationHandler(HTTPAdapter):
    def __init__(self, auth_provider: AuthProviderBase, auth_provider_options=None):
        super().__init__()

        self.auth_provider = auth_provider
        self.auth_provider_options = auth_provider_options
        self.next = None

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        scopes = self._get_middleware_options(request)

        if scopes:
            self.auth_provider.scopes = scopes

        token = self.auth_provider.get_access_token()
        request.headers.update({'Authorization': 'Bearer {}'.format(token)})

        if self.next is None:
            return super().send(request, stream, timeout, verify, cert, proxies)

        return self.next.send(request, stream, timeout, verify, cert, proxies)

    def _get_middleware_options(self, request):
        options = request.middleware_control.get(AUTH_MIDDLEWARE_OPTIONS) or self.auth_provider_options
        return options.scopes

