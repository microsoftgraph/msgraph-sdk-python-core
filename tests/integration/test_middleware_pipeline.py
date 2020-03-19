import warnings
from unittest import TestCase

from src.core.http_client_factory import HTTPClientFactory

from src.middleware.authorization_provider import AuthProviderBase
from src.middleware.authorization_handler import AuthorizationHandler



class MiddlewarePipelineTest(TestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")

    def test_middleware_pipeline(self):
        url = 'https://proxy.apisandbox.msdn.microsoft.com/svc?url=https://graph.microsoft.com/v1.0/me'

        authProvider = _CustomAuthProvider()
        authHandler = AuthorizationHandler(authProvider)

        middlewares = [
            authHandler
        ]

        requests = HTTPClientFactory.with_graph_middlewares(middlewares)
        result = requests.get(url)
        requests.close()

        self.assertEqual(result.status_code, 200)


class _CustomAuthProvider(AuthProviderBase):

    def get_access_token(self):
        return '{token:https://graph.microsoft.com/}'



