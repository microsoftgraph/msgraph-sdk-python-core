from msgraphcore.constants import AUTH_MIDDLEWARE_OPTIONS
from ..options.auth_middleware_options import AuthMiddlewareOptions


class MiddlewareControl:
    def __init__(self):
        self.middleware_options = {}

    def set(self, middleware_option_name, middleware_option):
        self.middleware_options.update({middleware_option_name: middleware_option})

    def get(self, middleware_option_name):
        return self.middleware_options.get(middleware_option_name, None)

    def get_middleware_options(self, func):
        self._reset_middleware_options()

        def wrapper(*args, **kwargs):
            scopes = kwargs.pop('scopes')
            self.set(AUTH_MIDDLEWARE_OPTIONS, AuthMiddlewareOptions(scopes))
            return func(*args, **kwargs)
        return wrapper

    def _reset_middleware_options(self):
        self.middleware_options = {}


middleware_control = MiddlewareControl()
