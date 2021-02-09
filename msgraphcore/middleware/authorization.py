from ..constants import AUTH_MIDDLEWARE_OPTIONS
from .abc_token_credential import TokenCredential
from .middleware import BaseMiddleware
from .options.middleware_control import middleware_control


class AuthorizationHandler(BaseMiddleware):
    def __init__(self, credential: TokenCredential, scopes: [str]):
        super().__init__()
        self.credential = credential
        self.scopes = scopes
        self.retry_count = 0

    def send(self, request, **kwargs):
        request.headers.update({'Authorization': 'Bearer {}'.format(self._get_access_token())})
        response = super().send(request, **kwargs)

        # Token might have expired just before transmission, retry the request one more time
        if response.status_code == 401 and self.retry_count < 2:
            self.retry_count += 1
            return self.send(request, **kwargs)
        return response

    def _get_access_token(self):
        return self.credential.get_token(*self.get_scopes())[0]

    def get_scopes(self):
        # Checks if there are any options for this middleware
        auth_options_present = middleware_control.get(AUTH_MIDDLEWARE_OPTIONS)
        # If there is, get the scopes from the options
        if auth_options_present:
            return auth_options_present.scopes
        else:
            return self.scopes
