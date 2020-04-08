from unittest import TestCase

from msgraphcore.middleware.options.auth_middleware_options import AuthMiddlewareOptions


class TestMiddlewareOptions(TestCase):
    def test_multiple_scopes(self):
        graph_scopes = 'https://graph.microsoft.com/v1.0?scopes=mail.read%20user.read%20'
        auth_options = AuthMiddlewareOptions(scopes=['mail.read', 'user.read'])
        self.assertEqual(auth_options.scopes, graph_scopes)
