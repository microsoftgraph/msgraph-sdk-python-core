from typing import Dict
from msgraphcore.constants import AUTH_MIDDLEWARE_OPTIONS
from msgraphcore.middleware.options.auth_middleware_options import AuthMiddlewareOptions


class MiddlewareControl(Dict):
    def __init__(self, **kwargs):
        self.middleware_options = {}
        self.get_middleware_options(**kwargs)

    def set(self, name, middleware_option):
        if name == 'scopes':
            # Set middleware options, for use by middleware in the middleware pipeline
            self.set(AUTH_MIDDLEWARE_OPTIONS, AuthMiddlewareOptions(scopes))

    def get(self, middleware_option_name):
        return self.middleware_options.get(middleware_option_name, None)

    def get_middleware_options(self, **kwargs):
        self._reset_middleware_options()
        scopes = kwargs.pop('scopes', None)
        if scopes:
            # Set middleware options, for use by middleware in the middleware pipeline
            self.set(AUTH_MIDDLEWARE_OPTIONS, AuthMiddlewareOptions(scopes))

    def _reset_middleware_options(self):
        # Reset middleware, so that they are not persisted across requests
        self.middleware_options = {}