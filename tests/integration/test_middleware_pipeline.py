import warnings
from unittest import TestCase

from src.core.graph_session import GraphSession

from src.middleware.authorization_provider import AuthProviderBase
from src.middleware.authorization_handler import AuthorizationHandler
from src.middleware.options.auth_middleware_options import AuthMiddlewareOptions


class MiddlewarePipelineTest(TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")

    def test_middleware_pipeline(self):
        url = 'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'

        auth_provider = _CustomAuthProvider()
        options = AuthMiddlewareOptions(['user.read'])
        auth_handler = AuthorizationHandler(auth_provider, auth_provider_options=options)

        middleware = [
            auth_handler
        ]

        graph_session = GraphSession(middleware=middleware)
        result = graph_session.get(url)

        self.assertEqual(result.status_code, 200)


class _CustomAuthProvider(AuthProviderBase):

    def get_access_token(self):
        return '{token:https://graph.microsoft.com/}'



