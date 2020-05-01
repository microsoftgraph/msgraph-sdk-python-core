import unittest

from msgraphcore.constants import AUTH_MIDDLEWARE_OPTIONS
from msgraphcore.middleware.authorization import AuthorizationHandler
from msgraphcore.middleware.options.middleware_control import middleware_control
from msgraphcore.middleware.options.auth_middleware_options import AuthMiddlewareOptions


class TestAuthorizationHandler(unittest.TestCase):
    def test_auth_options_override_default_scopes(self):
        auth_option = ['email.read']
        default_scopes = ['.default']

        middleware_control.set(AUTH_MIDDLEWARE_OPTIONS, AuthMiddlewareOptions(auth_option))
        auth_handler = AuthorizationHandler(None, default_scopes)

        auth_handler_scopes = auth_handler.get_scopes()
        self.assertEqual(auth_option, auth_handler_scopes)

    def test_auth_handler_get_scopes_does_not_overwrite_default_scopes(self):
        auth_option = ['email.read']
        default_scopes = ['.default']

        middleware_control.set(AUTH_MIDDLEWARE_OPTIONS, AuthMiddlewareOptions(auth_option))
        auth_handler = AuthorizationHandler(None, default_scopes)
        auth_handler.get_scopes()

        self.assertEqual(auth_handler.scopes, default_scopes)


