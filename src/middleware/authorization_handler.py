from requests.adapters import HTTPAdapter
from ._base import AuthProviderBase


class AuthorizationHandler(HTTPAdapter):
    def __init__(self, auth_provider: AuthProviderBase):
        super().__init__()

        self.auth_provider = auth_provider
        self.next=None

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        token = self.auth_provider.get_access_token()

        request.headers.update({'Authorization': 'Bearer {}'.format(token)})

        if self.next is None:
            return super().send(request, stream, timeout, verify, cert, proxies)

        return self.next.send(request, stream, timeout, verify, cert, proxies)
