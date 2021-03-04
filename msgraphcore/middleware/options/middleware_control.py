from msgraphcore.constants import AUTH_MIDDLEWARE_OPTIONS, RETRY_MIDDLEWARE_OPTIONS
from msgraphcore.middleware.options.auth_middleware_options import AuthMiddlewareOptions
from msgraphcore.middleware.options.retry_middleware_options import RetryMiddlewareOptions


class MiddlewareControl:
    def __init__(self):
        self.middleware_options = {}

    def set(self, middleware_option_name, middleware_option):
        self.middleware_options.update({middleware_option_name: middleware_option})

    def get(self, middleware_option_name):
        return self.middleware_options.get(middleware_option_name, None)

    def get_middleware_options(self, func):
        def wrapper(*args, **kwargs):
            # Get middleware options from **kwargs
            self._reset_middleware_options()
            scopes = kwargs.pop('scopes', None)
            if scopes:
                # Set middleware options, for use by middleware in the middleware pipeline
                self.set(AUTH_MIDDLEWARE_OPTIONS, AuthMiddlewareOptions(scopes))
            retry_configs = kwargs.pop('retry_config', None)
            if retry_configs:
                self.set(RETRY_MIDDLEWARE_OPTIONS, RetryMiddlewareOptions(retry_configs))
            return func(*args, **kwargs)

        return wrapper

    def _reset_middleware_options(self):
        # Reset middleware, so that they are not persisted across requests
        self.middleware_options = {}


middleware_control = MiddlewareControl()
